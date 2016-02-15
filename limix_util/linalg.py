import numpy as np
from scipy.linalg import solve_triangular
from scipy.linalg import cho_solve as sp_cho_solve
from numpy.linalg import LinAlgError

# Performs np.tr(dot(A, B))
def trace2(A, B):
    assert len(A.shape)==2 and len(B.shape)==2
    assert A.shape[1]==B.shape[0] and A.shape[0]==B.shape[1]
    return np.sum(A.T*B)

# def mctrace2(mv, n=100):
#     n1 = A.shape[0]
#     W = np.random.randn(n1, n)
#     R = mv(W)
#     return np.sum(W * R) / float(n)

def dotd(A, B):
    """Multiply two matrices and return the
    resulting diagonal.
    If A is nxp and B is pxn, it is done in O(pn).
    """
    return np.sum(A * B.T,1)

def ddot(d, mtx, left=True):
    """Multiply a full matrix by a diagonal matrix.
    This function should always be faster than dot.

    Input:
      d -- 1D (N,) array (contains the diagonal elements)
      mtx -- 2D (N,N) array

    Output:
      ddot(d, mts, left=True) == dot(diag(d), mtx)
      ddot(d, mts, left=False) == dot(mtx, diag(d))
    """
    if left:
        return (d*mtx.T).T
    else:
        return d*mtx

def colvec(a):
    assert isinstance(a, np.ndarray)
    assert a.ndim == 1
    return np.reshape(a, (-1, a.size)).T

# A is a full matrix and D is an array representing
# a diagonal matrix or a real number representing
# a diagonal matrix as well.
def sum2diag_inplace(A, D):
    np.fill_diagonal(A, np.diag(A) + D)

def sum2diag(A, D):
    R = A.copy()
    np.fill_diagonal(R, np.diag(A) + D)
    return R

def check_definite_positiveness(A):
    B = np.empty_like(A)
    B[:] = A
    B[np.diag_indices_from(B)] += np.sqrt(np.finfo(np.float).eps)
    try:
        np.linalg.cholesky(B)
    except np.linalg.LinAlgError:
        return False
    return True

def check_symmetry(A):
    return abs(A-A.T).max() < np.sqrt(np.finfo(np.float).eps)

def kl_divergence(p,q):
    return np.sum(np.log(p/q)*p)

def stl(a, b):
    return solve_triangular(a, b, lower=True, check_finite=False)

def stu(a, b):
    return solve_triangular(a, b, lower=False, check_finite=False)

def lu_slogdet(LU):
    adet = np.sum(np.log(np.abs(LU[0].diagonal())))

    sign = np.prod(np.sign(LU[0].diagonal()))

    nrows_exchange = LU[1].size - np.sum(LU[1] == np.arange(LU[1].size, dtype='int32'))

    odd = nrows_exchange % 2 == 1
    if odd:
        sign *= -1.0

    return (sign, adet)

def cho_solve(L, x):
    return sp_cho_solve((L, True), x, check_finite=False)

def tri_solve(L, x):
    return solve_triangular(L, x, lower=True, check_finite=False)

def _solve(A, B, jitter=np.sqrt(np.finfo(float).eps)):
    try:
        return np.linalg.solve(A, B)
    except LinAlgError:
        # print 'Warning: %s. Trying now with some jitter.' % str(e)
        A = sum2diag(A, np.ones(A.shape[0]) * jitter)
        return np.linalg.solve(A, B)

def solve(A, B):
    if A.shape[0] == 1:
        A_ = np.array([[ 1./A[0,0] ]])
        return np.dot(A_, B)
        # return B / A[0,0]
    elif A.shape[0] == 2:
        a = A[0,0]
        b = A[0,1]
        c = A[1,0]
        d = A[1,1]
        A_ = np.array([[d, -b], [-c, a]])
        A_ /= a*d - b*c
        return np.dot(A_, B)
    return _solve(A, B)


# def solve_4x4(A, B):
#     # public function invert() : Matrix4 {
#     # var m : Matrix4 = new Matrix4();
#
#     var s0 : Number = i00 * i11 - i10 * i01;
#     var s1 : Number = i00 * i12 - i10 * i02;
#     var s2 : Number = i00 * i13 - i10 * i03;
#     var s3 : Number = i01 * i12 - i11 * i02;
#     var s4 : Number = i01 * i13 - i11 * i03;
#     var s5 : Number = i02 * i13 - i12 * i03;
#
#     var c5 : Number = i22 * i33 - i32 * i23;
#     var c4 : Number = i21 * i33 - i31 * i23;
#     var c3 : Number = i21 * i32 - i31 * i22;
#     var c2 : Number = i20 * i33 - i30 * i23;
#     var c1 : Number = i20 * i32 - i30 * i22;
#     var c0 : Number = i20 * i31 - i30 * i21;
#
#     // Should check for 0 determinant
#
#     var invdet : Number = 1 / (s0 * c5 - s1 * c4 + s2 * c3 + s3 * c2 - s4 * c1 + s5 * c0);
#
#     m.i00 = (i11 * c5 - i12 * c4 + i13 * c3) * invdet;
#     m.i01 = (-i01 * c5 + i02 * c4 - i03 * c3) * invdet;
#     m.i02 = (i31 * s5 - i32 * s4 + i33 * s3) * invdet;
#     m.i03 = (-i21 * s5 + i22 * s4 - i23 * s3) * invdet;
#
#     m.i10 = (-i10 * c5 + i12 * c2 - i13 * c1) * invdet;
#     m.i11 = (i00 * c5 - i02 * c2 + i03 * c1) * invdet;
#     m.i12 = (-i30 * s5 + i32 * s2 - i33 * s1) * invdet;
#     m.i13 = (i20 * s5 - i22 * s2 + i23 * s1) * invdet;
#
#     m.i20 = (i10 * c4 - i11 * c2 + i13 * c0) * invdet;
#     m.i21 = (-i00 * c4 + i01 * c2 - i03 * c0) * invdet;
#     m.i22 = (i30 * s4 - i31 * s2 + i33 * s0) * invdet;
#     m.i23 = (-i20 * s4 + i21 * s2 - i23 * s0) * invdet;
#
#     m.i30 = (-i10 * c3 + i11 * c1 - i12 * c0) * invdet;
#     m.i31 = (i00 * c3 - i01 * c1 + i02 * c0) * invdet;
#     m.i32 = (-i30 * s3 + i31 * s1 - i32 * s0) * invdet;
#     m.i33 = (i20 * s3 - i21 * s1 + i22 * s0) * invdet;
#
#     return m;
#     }





_MIN_EIGVAL = np.sqrt(np.finfo(float).eps)

def _QS_from_K(K):
    (S, Q) = np.linalg.eigh(K)
    ok = S >= _MIN_EIGVAL
    S = S[ok]
    Q = Q[:, ok]
    return (Q, S)

def _QS_from_G(G):
    (Q, Ssq, _) = np.linalg.svd(G, full_matrices=False)
    S = Ssq**2
    return (Q, S)

# which: 'G' or 'K'
# return Q, S such that:
#   K = dot(dot(Q, S[:,np.newaxis]), Q.T)
#   dot(G, G.T) = dot(dot(Q, S[:,np.newaxis]), Q.T)
def economic_QS(GK, which):
    assert isinstance(which, str)
    if which == 'G':
        G = GK
        K = None
    elif which == 'K':
        G = None
        K = GK
    elif which == 'GK':
        G = GK[0]
        K = GK[1]
    elif which == 'KG':
        G = GK[1]
        K = GK[0]
    else:
        assert False, 'Unrecognized matrix type %s.' % which

    if G is None:
        return _QS_from_K(K)

    if K is None:
        if G.shape[1] >= G.shape[0]:
            K = np.dot(G, G.T)
            return _QS_from_K(K)
        return _QS_from_G(G)

    if G.shape[1] >= G.shape[0]:
        return _QS_from_K(K)
    return _QS_from_G(G)
