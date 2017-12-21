import sys
import numpy as np
sys.path.append("/home/disliu/ffthompy-sparse")

from ffthompy.tensors import TensorFuns
from scipy.linalg import block_diag
import numpy.fft as fft


class Tucker(TensorFuns):

    def __init__(self, name='', core=None, basis=None, Fourier=False,
                 r=[3,3], N=[5,5], randomise=False):
        self.name=name
        self.Fourier=Fourier
        if core is not None and basis is not None:
            self.order=basis.__len__()
            self.basis=basis
            self.core=core
            self.r=np.empty(self.order)
            self.N=np.empty(self.order)
            for ii in range(self.order):
                self.r[ii],self.N[ii]=basis[ii].shape
        else:
            self.order=r.__len__()
            self.r=np.array(r)
            self.N=np.array(N)
            if randomise:
                self.randomise()
            else:
                self.core=np.zeros(r)
                self.basis=[np.zeros([self.r[ii],self.N[ii]]) for ii in range(self.order)]

    def randomise(self):
        self.core=np.random.random(self.r)
        self.basis=[np.random.random([self.r[ii],self.N[ii]]) for ii in range(self.order)]

    def __add__(self, Y, tol=None, rank=None):
        X=self
        core= block_diag(X.core,Y.core)
        basis=[np.vstack([X.basis[ii],Y.basis[ii]]) for ii in range(X.order)]
        return Tucker(name=X.name+'+'+Y.name, core=core, basis=basis)

    def __neg__(self):
        return Tucker(core=-self.core, basis=self.basis)

    def __mul__(self, Y, tol=None, rank=None):
        "element-wise multiplication of two Tucker tensors"
        X = self
        new_r=X.r*Y.r
        A=X.basis[0]
        B=X.basis[1]
        A2=Y.basis[0]
        B2=Y.basis[1]

        newA=np.zeros((new_r[0], X.N[0]))
        newB=np.zeros((new_r[1], X.N[1]))
        for i in range(0, X.r[0]):
            for j in range(0, Y.r[0]):
                newA[i*Y.r[0]+j, :]=A[i, :]*A2[j, :]

        for i in range(0, X.r[1]):
            for j in range(0, Y.r[1]):
                newB[i*Y.r[1]+j, :]=B[i, :]*B2[j, :]

        newC=np.kron(X.core, Y.core)

        newBasis=[newA, newB]

        return (Tucker(name='a*b', core=newC, basis=newBasis))

    def fourier(self):
        "(inverse) discrete Fourier transform"
        if self.Fourier:
            fftfun=lambda Fx, N: fft.fftshift(fft.ifft(fft.ifftshift(Fx, axes=1), axis=1), axes=1)*N
        else:
            fftfun=lambda x, N: fft.fftshift(fft.fft(fft.ifftshift(x, axes=1), axis=1), axes=1)/N

        basis=[]
        for ii in range(self.order):
            basis.append(fftfun(self.basis[ii], self.N[ii]))

        return Tucker(core=self.core, basis=basis, Fourier=not self.Fourier)

    def ifourier(self):
        "inverse discrete Fourier transform"
        raise NotImplementedError()

    def full(self):
        "return a full tensor"
        if self.order==2:
            return np.einsum('ij,ik,jl->kl', self.core, self.basis[0],self.basis[1])
        else:
            raise NotImplementedError()

    def truncate(self, tol=None, rank=None):
        "return truncated tensor"
        raise NotImplementedError()

    def __repr__(self, full=False, detailed=False):
        keys = ['name', 'Fourier', 'N', 'r']
        ss = "Class : {0}({1}) \n".format(self.__class__.__name__, self.order)
        skip = 4*' '
        nstr = np.array([key.__len__() for key in keys]).max()

        for key in keys:
            attr = getattr(self, key)
            if callable(attr):
                ss += '{0}{1}{3} = {2}\n'.format(skip, key, str(attr()), (nstr-key.__len__())*' ')
            else:
                ss += '{0}{1}{3} = {2}\n'.format(skip, key, str(attr), (nstr-key.__len__())*' ')

        return ss


if __name__=='__main__':
    N=np.array([5,5])
    a = Tucker(name='a', r=np.array([2,3]), N=N, randomise=True)
    b = Tucker(name='b', r=np.array([4,5]), N=N, randomise=True)
    print(a)
    print(b)

    # addition
    c = a+b
    print(c)
    c2 = a.full()+b.full()
    print(np.linalg.norm(c.full()-c2))

    # multiplication
    c = a*b
    c2 = a.full()*b.full()
    print(np.linalg.norm(c.full()-c2))

    #DFT
    from ffthompy.operators import DFT
    Fa = a.fourier()
    print(Fa)
    Fa2 = DFT.fftnc(a.full(), a.N)
    print(np.linalg.norm(Fa.full()-Fa2))
    print('END')