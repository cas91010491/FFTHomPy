import numpy as np
import scipy.sparse.linalg as sp
import itertools
import sys
# from ffthompy.general.solver import richardson

# PARAMETERS ##############################################################
dim  = 2            # number of dimensions (works for 2D and 3D)
N     = dim*(5,)    # number of voxels (assumed equal for all directions)
calc_eigs = 1

maxiter=3

# auxiliary values
prodN = np.prod(np.array(N)) # number of grid points
ndof  = dim*prodN # number of degrees-of-freedom
vec_shape=(dim,)+N # shape of the vector for storing DOFs

# PROBLEM DEFINITION ######################################################
# A = np.einsum('ij,...->ij...',np.eye(dim),1.+10.*np.random.random(N)) # material coefficients
phase  = np.ones(N); phase[:3,:3] = 10.
A = np.einsum('ij,...->ij...', np.eye(dim), phase)
E = np.zeros(vec_shape); E[0] = 1. # set macroscopic loading

# PROJECTION IN FOURIER SPACE #############################################
Ghat = np.zeros((dim,dim)+ N) # zero initialize
freq = [np.arange(-(N[ii]-1)/2.,+(N[ii]+1)/2.) for ii in range(dim)]
for i,j in itertools.product(range(dim),repeat=2):
    for ind in itertools.product(*[range(n) for n in N]):
        q = np.empty(dim)
        for ii in range(dim):
            q[ii] = freq[ii][ind[ii]]  # frequency vector
        if not q.dot(q) == 0:          # zero freq. -> mean
            Ghat[i,j][ind] = -(q[i]*q[j])/(q.dot(q))

# OPERATORS ###############################################################
dot21  = lambda A,v: np.einsum('ij...,j...  ->i...',A,v)
fft    = lambda V: np.fft.fftshift(np.fft.fftn (np.fft.ifftshift(V),N))/np.prod(N)
ifft   = lambda V: np.fft.fftshift(np.fft.ifftn(np.fft.ifftshift(V),N))*np.prod(N)
G_fun  = lambda V: np.real(ifft(dot21(Ghat,fft(V)))).reshape(-1)
A_fun  = lambda v: dot21(A,v.reshape(vec_shape))
GA_fun = lambda v: G_fun(A_fun(v))

# CONJUGATE GRADIENT SOLVER ###############################################
b = -GA_fun(E) # right-hand side
e, _=sp.cg(A=sp.LinearOperator(shape=(ndof, ndof), matvec=GA_fun, dtype='float'), b=b)

aux = e+E.reshape(-1)
# print('auxiliary field for macroscopic load E = {1}:\n{0}'.format(aux.reshape(vec_shape),
#                                                                   format((1,)+(dim-1)*(0,))))
print('homogenised properties A11 = {}'.format(np.inner(A_fun(aux).reshape(-1), aux)/prodN))

### POTENTIAL SOLVER in real space #####################################################################
print('\n== Potential solver in real space =======================')
# GRADIENT IN FOURIER SPACE #############################################
hGrad = np.zeros((dim,)+ N) # zero initialize
freq = [np.arange(-(N[ii]-1)/2.,+(N[ii]+1)/2.) for ii in range(dim)]
for ind in itertools.product(*[range(n) for n in N]):
    for i in range(dim):
        hGrad[i][ind] = freq[i][ind[i]]
hGrad = -hGrad*2*np.pi*1j

k2 = np.einsum('i...,i...', hGrad, np.conj(hGrad)).real
from ffthompy.matvec import mean_index
k2[mean_index(N)]=1.

# OPERATORS ###############################################################
FGrad = lambda Fu: np.einsum('i...,...->i...', hGrad, Fu)
FDiv = lambda Fe: np.einsum('i...,i...->...', hGrad, Fe)
Grad = lambda u: ifft(FGrad(fft(u))).real
Div = lambda e: ifft(FDiv(fft(e))).real
DivAGrad_fun = lambda u: Div(dot21(A, Grad(u.reshape(N)))).ravel()

# CONJUGATE GRADIENT SOLVER ###############################################
b = -Div(dot21(A,E)).ravel() # right-hand side
u, _=sp.cg(A=sp.LinearOperator(shape=(prodN, prodN), matvec=DivAGrad_fun, dtype='float'), b=b)

e = Grad(u.reshape(N))
aux = e+E
print('homogenised properties A11 = {}'.format(np.sum(dot21(A,aux)*aux)/prodN))

if calc_eigs:
    print('calculating eigenvalues...')
    linoper=sp.LinearOperator(shape=(prodN, prodN), matvec=DivAGrad_fun, dtype='float')
    eigs_min = sp.eigsh(linoper, k=2, which='SM', return_eigenvectors=False)
    eigs_max = sp.eigsh(linoper, k=1, which='LM', return_eigenvectors=False)
    print('min(eigs)={0}; max(eigs)={1}'.format(eigs_min, eigs_max))
    print('cond={}'.format(eigs_max/eigs_min[0]))

### POTENTIAL SOLVER in Fourier space #####################################################################
print('\n== Potential solver in Fourier space =======================')
GFAFG_fun = lambda Fu: -FDiv(fft(dot21(A, ifft(FGrad(Fu)))))
GFAFG_funvec = lambda Fu: GFAFG_fun(Fu.reshape(N)).ravel()
B = FDiv(fft(dot21(A,E))) # right-hand side

linoper=sp.LinearOperator(shape=(prodN, prodN), matvec=GFAFG_funvec, dtype='complex')
Fu, _=sp.cg(A=linoper, b=B.ravel())

e = ifft(FGrad(Fu.reshape(N))).real
aux = e+E
print('homogenised properties A11 = {}'.format(np.sum(dot21(A,aux)*aux)/prodN))
if calc_eigs:
    print('calculating eigenvalues...')
    eigs_min = sp.eigsh(linoper, k=2, which='SM', return_eigenvectors=False)
    eigs_max = sp.eigsh(linoper, k=1, which='LM', return_eigenvectors=False)[0]
    print('min(eigs)={0}; max(eigs)={1}'.format(eigs_min, eigs_max))
    print('cond={}'.format(eigs_max/eigs_min[0]))

print('== Richardson iteration ====================================')
par={'alpha': (eigs_min[0]+eigs_max)/2,
     'maxiter': maxiter,
     'tol': 1e-6}

def richardson(Afun, B, x0=None, par=None, callback=None, norm=None):
    if isinstance(par['alpha'], float):
        omega = 1./par['alpha']
    else:
        raise NotImplementedError()
    res = {'norm_res': [],
           'kit': 0}
    if x0 is None:
        x=B*omega
    else:
        x = x0

    if norm is None:
        norm = lambda X: float(X.T*X)**0.5
    norm_res=1e15
    while (norm_res > par['tol'] and res['kit'] < par['maxiter']):
        res['kit'] += 1
        residuum=B-Afun(x)
        x = x + residuum*omega
        norm_res=norm(residuum)
        res['norm_res'].append(norm_res)
    res['norm_res'].append(norm(B-Afun(x)))
    return x, res

Fu2, res2 = richardson(Afun=GFAFG_fun, B=B, x0=None, par=par, norm=np.linalg.norm)
print('norm(dif)={}'.format(np.linalg.norm(Fu-Fu2.ravel())))
print('norm(res)={}'.format(res2['norm_res']))
print('norm(res)={}'.format(np.linalg.norm(B-GFAFG_fun(Fu2))))

### PRECONDITIONING in Fourier space #####################################################################
print('== Solver with preconditioning =========================================')
Pfun = lambda X: X/k2
PGFAFG_fun=lambda X: Pfun(GFAFG_fun(X))

if calc_eigs:
    PGFAFG_funvec=lambda Fu: PGFAFG_fun(Fu.reshape(N)).ravel()
    linoper=sp.LinearOperator(shape=(prodN, prodN), matvec=PGFAFG_funvec, dtype='complex')
    eigs_min = sp.eigsh(linoper, k=2, which='SM', return_eigenvectors=False)
    eigs_max = sp.eigsh(linoper, k=1, which='LM', return_eigenvectors=False)
    print('min(eigs)={0}; max(eigs)={1}'.format(eigs_min, eigs_max))
    print('cond={}'.format(eigs_max/eigs_min[0]))

parP = par.copy()
parP['alpha'] = (1.+10.)/2.
Fu3, res3 = richardson(Afun=PGFAFG_fun, B=Pfun(B), x0=None, par=parP, norm=np.linalg.norm)

print('norm(dif)={}'.format(np.linalg.norm(Fu-Fu3.ravel())))
print('norm(resP)={}'.format(res3['norm_res']))
print('norm(resP)={}'.format(np.linalg.norm(Pfun(B)-PGFAFG_fun(Fu3))))
print('norm(res)={}'.format(np.linalg.norm(B-GFAFG_fun(Fu3))))

print('\n== SPARSE solver =======================')
from ffthompy.sparse import decompositions
from ffthompy.sparse.canoTensor import CanoTensor

# matrix A
Abas, k, max_err = decompositions.dCA_matrix_input(A[0,0], k=3, tol=1e-14)
normAbas=np.linalg.norm(Abas, axis=0)
Abas = Abas/np.atleast_2d(normAbas)
Abas=Abas.T
As = CanoTensor(name='A', core=normAbas**2, basis=[Abas, Abas])

# Grad
hGrad_s = []
for ii in range(dim):
    basis=[]
    for jj in range(dim):
        if ii==jj:
            basis.append(np.atleast_2d(freq[jj]*2*np.pi*1j))
        else:
            basis.append(np.atleast_2d(np.ones(N[jj])))
    hGrad_s.append(CanoTensor(name='hGrad({})'.format(ii), core=np.array([1]), basis=basis,
                              Fourier=True))

# R.H.S.
Es = CanoTensor(name='E', core=np.array([1.]),
               basis=[np.atleast_2d(np.ones(N[ii])) for ii in range(dim)], Fourier=False)

Bs = -(hGrad_s[0]*(As*Es).fourier())
print(np.linalg.norm(B-Bs.full()))


# linear operator
def GFAFG_fun_s(Fx):
    GFx=[hGrad_s[ii]*Fx for ii in range(dim)]
    FGFx=[GFx[ii].fourier() for ii in range(dim)]
    AFGFx=[As*FGFx[ii] for ii in range(dim)]
    FAFGFx=[AFGFx[ii].fourier() for ii in range(dim)]
    GFAFGFx = hGrad_s[0]*FAFGFx[0]
    for ii in range(1,dim):
        GFAFGFx += hGrad_s[ii]*FAFGFx[ii]
    GFAFGFx.name='fun(x)'
#     GFAFGFx=GFAFGFx.truncate(rank=50)
    return -GFAFGFx

# testing
print('testing A...')
x = CanoTensor(name='a', r=4, N=N, randomise=True)
Fx=x.fourier()
res1 = GFAFG_fun_s(Fx)
res2 = GFAFG_fun(fft(x.full()))
print(np.linalg.norm(res1.full()-res2))
print(res1)

# solver
# norm = lambda X: X.norm(ord='core')
norm=lambda X: np.linalg.norm(X.full())

Fus, ress=richardson(Afun=GFAFG_fun_s, B=Bs, par=par, norm=norm)
Fus.name='Fus'

print('solver results...')
print Fus
print('norm(dif)={}'.format(np.linalg.norm(Fu-Fus.full().ravel())))
print('norm(res)={}'.format(ress['norm_res']))
print('norm(res)={}'.format(np.linalg.norm((Bs-GFAFG_fun_s(Fus)).full())))

print('\n== SPARSE solver with preconditioner =======================')
# preconditioner
from scipy.linalg import svd
U,S,Vh = sp.svds(1./k2, k=4)
# U,S,Vh = svd(1./k2)

print('singular values={}'.format(S))

Ps = CanoTensor(name='P', core=S[:3], basis=[U[:,:3].T, Vh[:3]], Fourier=True)
print('norm(P-Ps)={}'.format(np.linalg.norm(1./k2-Ps.full())))

def PGFAFG_fun_s(Fx):
    R=GFAFG_fun_s(Fx)
    R=Ps*R
    R=R.truncate(tol=1e-2)
#     R=R.truncate(rank=1000)
    return R

PBs=Ps*Bs
Fus, ress=richardson(Afun=PGFAFG_fun_s, B=PBs, par=parP, norm=norm)
Fus.name='Fus'

print('solver results...')
print Fus
print('norm(dif)={}'.format(np.linalg.norm(Fu-Fus.full().ravel())))
print('norm(resP)={}'.format(ress['norm_res']))
print('norm(resP)={}'.format(np.linalg.norm((PBs-PGFAFG_fun_s(Fus)).full())))
print('norm(res)={}'.format(np.linalg.norm((Bs-GFAFG_fun_s(Fus)).full())))

U, S, Vh=svd(Fus.full())

print('sing. vals of solution={}'.format(S))

print('END')
