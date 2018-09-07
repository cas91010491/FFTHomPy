import numpy as np
from ffthompy.sparse.objects.tensors import SparseTensorFuns

import timeit

class CanoTensor(SparseTensorFuns):

    def __init__(self, name='unnamed', val=None, core=None, basis=None, orthogonal=False, Fourier=False,
                 r=None, N=None, randomise=False):

        self.name=name
        self.Fourier=Fourier # TODO: dtype instead of Fourier
        self.orthogonal=orthogonal
        
        if val is not None:
            if len(val.shape)==2:
                u, s, vt=np.linalg.svd(val, full_matrices=0)
                
                self.order= 2
                self.basis=[u.T, vt]
                self.core=s
                self.r=self.core.shape[0]  
    
                self.N=np.empty(self.order, dtype=np.int)
                for ii in range(self.order):
                    self.N[ii]=self.basis[ii].shape[1]         
            else:
                raise ValueError("Canonical format not applicable to tensors higher than 2 dimensional.")
        
        elif core is not None and basis is not None:
            self.order=basis.__len__()
            self.basis=basis
            
            if len(core.shape)==2:
                self.core=np.diag(core)
            else:
                self.core=core
                
            self.r=basis[0].shape[0] # since all basis share the same r

            self.N=np.empty(self.order, dtype=np.int)
            for ii in range(self.order):
                self.N[ii]=basis[ii].shape[1]
        else:
            self.r=3
            self.N=[5,5]
            self.order=self.N.__len__()
            if randomise:
                self.randomise()
                self.sort()
            else:
                self.core=np.zeros(r)
                self.basis=[np.zeros([self.r[ii], self.N[ii]]) for ii in range(self.order)]

    def randomise(self):
        self.core=np.random.random((self.r,))
        self.basis=[np.random.random([self.r, self.N[ii]]) for ii in range(self.order)]

    def orthogonalise(self):
        """re-orthogonalise the basis"""
        # re-orthogonalise the basis by QR and SVD
        qa, ra=np.linalg.qr(self.basis[0].T)
        qb, rb=np.linalg.qr(self.basis[1].T)

        core=ra*self.core[np.newaxis, :]
        core=np.dot(core, rb.T)

        u, s, vt=np.linalg.svd(core, full_matrices=0)

        newA=np.dot(qa, u)
        newB=np.dot(vt, qb.T)

        newBasis=[newA.T, newB]

        return CanoTensor(name=self.name, core=s, basis=newBasis, orthogonal=True, Fourier=self.Fourier)

    def __add__(self, Y):
        X=self
        assert(X.Fourier==Y.Fourier)
        core=np.hstack([X.core, Y.core])
        basis=[np.vstack([X.basis[ii], Y.basis[ii]]) for ii in range(self.order)]

        return CanoTensor(name=X.name+'+'+Y.name, core=core, basis=basis, Fourier=self.Fourier).orthogonalise()

    def __mul__(self, Y):
        "element-wise multiplication of two canonical tensors"

        if isinstance(Y, float) or isinstance(Y, int) :
            R=self.copy()
            R.core=self.core*Y
            return R
        elif isinstance(Y, np.ndarray) and Y.shape==(1,):
            R=self.copy()
            R.core=self.core*Y[0]
            return R

        else:
            X=self
            if X.Fourier:
                dtype=np.complex
            else:
                dtype=np.float

            new_r=X.r*Y.r

            A=X.basis[0]
            B=X.basis[1]
            A2=Y.basis[0]
            B2=Y.basis[1]

            newA=np.zeros((new_r, X.N[0]), dtype=dtype)
            newB=np.zeros((new_r, X.N[1]), dtype=dtype)
            coeff=np.zeros((new_r,))

            for i in range(0, X.r):
                for j in range(0, Y.r):
                    newA[i*Y.r+j, :]=A[i, :]*A2[j, :]
                    newB[i*Y.r+j, :]=B[i, :]*B2[j, :]
                    coeff[i*Y.r+j]=X.core[i]*Y.core[j]

            return CanoTensor(name=X.name+'*'+Y.name, core=coeff, basis=[newA, newB],
                              Fourier=self.Fourier).orthogonalise()

    def full(self):
        "return a full tensor"
        if self.order==2:
            return np.einsum('i,ik,il->kl', self.core, self.basis[0], self.basis[1])
#             return(np.dot(np.dot(self.basis[0].T, self.core), self.basis[1]))
        else:
            raise NotImplementedError()

    def sort(self):
        "The function sort the modes in accordance with the magnitude of core"
        inds = np.flip(np.argsort(np.abs(self.core), kind='mergesort'), 0)
        self.core=self.core[inds]
        for ii in range(self.order):
            self.basis[ii] = self.basis[ii][inds]

    def truncate(self, rank=None, tol=None):
        "return truncated tensor"
        # tol is the maximum "portion" of the core trace to be lost, e.g. tol=0.01 means at most 1 percent could be lost in the truncation.
        # if tol is not none, it will override rank as the truncation criteria.
        basis=list(self.basis) # this copying avoids perturbation to the original tensor object
        core=self.core

        if rank>self.r:
            #print ("Warning: Rank of the truncation not smaller than the original rank, truncation aborted!")
            return self

        # to determine the rank of truncation
        if tol is None and rank is None:
            return self
        elif tol is not None:
            # determine the truncation rank so that (1.0-tol)*100% of the trace of the core is perserved.
            rank=np.searchsorted(np.cumsum(np.abs(core))/np.sum(np.abs(core)), 1.0-tol)+1

        # truncation
        core=core[:rank] # it is already sorted in case of using svd
        for ii in range(self.order):
            basis[ii]=basis[ii][:rank, :]

        return CanoTensor(name=self.name+'_truncated', core=core, basis=basis, Fourier=self.Fourier)

    def norm(self, ord='fro'):
        if ord=='fro':
            R=self*self.conj()
            val=0.
            for ii in range(R.r):
                valii=R.core[ii]
                for jj in range(R.order):
                    valii*=np.sum(R.basis[jj][ii]).real
                val+=valii
            val=val**0.5
        elif ord==1:
            pass
        elif ord=='inf':
            pass
        elif ord=='core':
            return np.linalg.norm(self.core)

        else:
            raise NotImplementedError()
        return val

    def mean(self):
        R=self
        val=0.
        for ii in range(R.r):
            valii=R.core[ii]
            for jj in range(R.order):
                valii*=np.sum(R.basis[jj][ii])
            val+=valii
        return val

    def enlarge(self, M):
        dtype=self.basis[0].dtype
        assert(self.Fourier==True)

        M=np.array(M, dtype=np.int)
        N=np.array(self.N)

        if np.allclose(M, N):
            return self

        # dim = N.size
        ibeg=np.ceil(np.array(M-N, dtype=np.float)/2).astype(dtype=np.int)
        iend=np.ceil(np.array(M+N, dtype=np.float)/2).astype(dtype=np.int)

        basis=[]
        for ii, m in enumerate(M):
            basis.append(np.zeros([self.r, m], dtype=dtype))
            basis[ii][:, ibeg[ii]:iend[ii]]=self.basis[ii]

        newOne=self.copy()
        newOne.basis=basis
        newOne.N=[None]*newOne.order
        for i in range(newOne.order):
            newOne.N[i]=newOne.basis[i].shape[1]
        # return CanoTensor(name=self.name, core=self.core, basis=basis, Fourier=self.Fourier)
        return newOne # this avoid using specific class name, e.g. canoTensor, so that can be shared by tucker and canoTensor

    def __neg__(self):
        newOne=self.copy()
        newOne.core=-newOne.core
        return newOne # this avoid using specific class name, e.g. canoTensor, so that can be shared by tucker and canoTensor
        # return Tucker(core=-self.core, basis=self.basis, Fourier=self.Fourier)

    def __sub__(self, Y):
        return self.__add__(-Y)

    def __rmul__(self, X):

        if isinstance(X, np.float) or isinstance(X, np.int) :
            R=self.copy()
            R.core=X*self.core
        else:
            raise NotImplementedError()
        return R

    def conj(self):
        """Element-wise complex conjugate"""
        basis=[]
        for ii in range(self.order):
            basis.append(self.basis[ii].conj())
        res=self.copy()
        res.basis=basis
        return res

    def decrease(self, M):
        assert(self.Fourier is True)

        M=np.array(M, dtype=np.int)
        N=np.array(self.N)
        assert(np.all(np.less(M, N)))

        ibeg=np.fix(np.array(N-M+(M%2), dtype=np.float)/2).astype(dtype=np.int)
        iend=np.fix(np.array(N+M+(M%2), dtype=np.float)/2).astype(dtype=np.int)

        basis=[]
        for ii in range(N.size):
            basis.append(self.basis[ii][:, ibeg[ii]:iend[ii]])

        newOne=self.copy()
        newOne.basis=basis
        newOne.N=np.zeros((newOne.order,), dtype=int)
        for i in range(newOne.order):
            newOne.N[i]=newOne.basis[i].shape[1]
        return newOne # this avoid using specific class name, e.g. canoTensor, so that can be shared by tucker and canoTensor
        # return Tucker(name=self.name, core=self.core, basis=basis, Fourier=self.Fourier)

    def add(self, Y, tol=None, rank=None):
        return (self+Y).truncate(tol=tol, rank=rank)

    def multiply(self, Y, tol=None, rank=None):
        # element-wise multiplication
        return (self*Y).truncate(tol=tol, rank=rank)


    def scal(self, Y):
        X = self
        assert(X.Fourier==Y.Fourier)
        XY = X*Y
        if X.Fourier:
            return XY.mean()
        else:
            return XY.mean()/np.prod(X.N)

    def repeat(self, M):
        """
        Enhance the tensor size from to N to M, by repeating all elements by M/N times.

        :param M: the new size .
        :type A: integer or list of integers

        :returns: Tucker -- a new tucker object with size M
        """
        if isinstance(M, int):
            M=M*np.ones((self.order,), dtype=int)

        if ((M.astype(float)/self.N)%1).any()!=0 :
            raise NotImplementedError("M is not a multiple of the old size N")

        res=self.copy()
        for i in range(self.order):
            res.basis[i]=np.repeat(res.basis[i], M[i]/self.N[i], axis=1)
            res.basis[i]/=np.sqrt(M[i]/self.N[i]) # restore original norm

        res.core*=np.prod(np.sqrt(M/self.N))
        res.N=M
        res.orthogonal=self.orthogonal

        return res

    def project(self, M):
        if self.Fourier:
            if all(M>=self.N):
                return self.enlarge(M)
            elif all(M<=self.N):
                return self.decrease(M)
        else:
            F=self.fourier()
            if all(M>=self.N):
                F=F.enlarge(M)
            elif all(M<=self.N):
                F=F.decrease(M)

            return F.fourier() # inverse Fourier

    def __repr__(self, full=False, detailed=False):
        keys=['name', 'Fourier', 'orthogonal', 'N', 'r']
        ss="Class : {0}({1}) \n".format(self.__class__.__name__, self.order)
        skip=4*' '
        nstr=np.array([key.__len__() for key in keys]).max()

        for key in keys:
            attr=getattr(self, key)
            if callable(attr):
                ss+='{0}{1}{3} = {2}\n'.format(skip, key, str(attr()), (nstr-key.__len__())*' ')
            else:
                ss+='{0}{1}{3} = {2}\n'.format(skip, key, str(attr), (nstr-key.__len__())*' ')

        return ss
    
    @property
    def size(self):
        "return the number of elements of the original full tensor"
        return np.prod(self.N)
 
    @property
    def memory(self):
        "return the number of floating point numbers that consist of the canonical tensor"
        return self.r +self.r*sum(self.N)

if __name__=='__main__':
#    N=[10,20]
#    a = CanoTensor(name='a', r=3, N=N, randomise=True)
#    b = CanoTensor(name='b', r=3, N=N, randomise=True)
#    print(a)
#    print(b)
#    # addition
#    c = a+b
#    print(c)
#    c2 = a.full()+b.full()
#    print(np.linalg.norm(c.full()-c2))
#    # multiplication
#
#    c = a*b
#    c2 = a.full()*b.full()
#    print(np.linalg.norm(c.full()-c2))

    # DFT
    ########################################## test with "smoother" matices
    N=10
    M=20
#    L= min(N,M)

    x=np.linspace(-np.pi, np.pi, M)
    y=np.linspace(-np.pi, 0.77*np.pi, N)
    # creat matrix for test
    S1=np.sin(x[np.newaxis, :]+y[:, np.newaxis])*(x[np.newaxis, :]+y[:, np.newaxis])
    S2=np.cos(2*x[np.newaxis, :]-y[:, np.newaxis])*(2*x[np.newaxis, :]-y[:, np.newaxis])
    #S1 = np.dot(np.reshape(x,(M,1)), np.reshape(y,(1,N))) + np.dot(np.sin(np.reshape(x,(M,1))), np.reshape(y,(1,N))**2)

    # factorize the matrix
    u1, s1, vt1=np.linalg.svd(S1, full_matrices=0)
    u2, s2, vt2=np.linalg.svd(S2, full_matrices=0)


    # construct  canoTensors with the normalized basis and the corresponding coefficients core
    a=CanoTensor(name='a', core=s1, basis=[u1.T, vt1])
    b=CanoTensor(name='b', core=s2, basis=[u2.T, vt2])
#     N=[100,101]
#     a=CanoTensor(name='a', r=50, N=N, randomise=True)
#     b=CanoTensor(name='a', r=60, N=N, randomise=True)

    # addition
    c=a+b
    c2=a.add(b, tol=1e-5)
    c2=c.truncate(tol=1e-5)

    c_add=a.full()+b.full()
    print
    print "(a+b).full - (a.full+b.full)    = ", (np.linalg.norm(c.full()-c_add))
    print "add(a,b).full - (a.full+b.full) = ", (np.linalg.norm(c2.full()-c_add))


    # multiplication

    c=a*b
    c3=a.multiply(b, tol=0.001)

    c_mul=a.full()*b.full()
    print
    print  "                  (a*b).full - (a.full*b.full) = ", (np.linalg.norm(c.full()-c_mul))
    print  "truncated multiply(a,b).full - (a.full*b.full) = ", (np.linalg.norm(c3.full()-c_mul))
    print

    print('rank control on tensor product:')
    print "full product tensor rank=     ", c.r
    print "truncated product tensor rank=", c3.r
    print
    # truncation
    a_trunc=a.truncate(rank=4)

    print  "a.full  - a_trunc.full        = ", np.linalg.norm(a.full()-a_trunc.full())
    print

    # DFT
    print('testing DFT...')

    from ffthompy.tensors.operators import DFT

    Fa=a.fourier()
    Fa2=DFT.fftnc(a.full(), a.N)

    print(np.linalg.norm(Fa.full()-Fa2))

    print('Comparing time cost of tensor of 1-D FFT and n-D FFT ...')
    t1=timeit.timeit("a.fourier()", setup='from __main__ import a', number=10)
    afull=a.full()
    t2=timeit.timeit("DFT.fftnc(afull, a.N)", setup='from ffthompy.tensors.operators import DFT;from __main__ import a, afull', number=10)
    # t1=timeit.timeit("aa=a.truncate(tol=0.05); aa.fourier()", setup='from __main__ import a', number=10000)
    print
    print "Tensor of 1D FFT costs: %f"%t1
    print "n-D FFT costs         : %f"%t2
    
    ### test enlarge#####
    n=3
#    T1= np.zeros((n,n, n))
#    T1[n/3:2*n/3, n/3:2*n/3, n/3:2*n/3]=1
    
    T1= np.zeros((n,n ))
    T1[n/3:2*n/3, n/3:2*n/3 ]=1
    
    u1, s1, vt1=np.linalg.svd(T1, full_matrices=0)
    
    t=CanoTensor(name='a', core=s1, basis=[u1.T, vt1])
    tf=t.fourier()
    tfl=tf.enlarge([3,5])
    tfli= tfl.fourier()
    
    print(tfli.full().real)

    print('END')
