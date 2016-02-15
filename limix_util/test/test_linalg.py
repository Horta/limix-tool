import unittest
import numpy as np
from limix_util.linalg import ddot, sum2diag

class TestEPGauss(unittest.TestCase):
    def setUp(self):
        self._random = np.random.RandomState(5304)

    def test_ddot(self):
        A = self._random.randn(2, 2)
        B = self._random.randn(2)
        C = np.array([[-0.93063708, -1.43422344],
                      [-0.01134216, -0.00920069]])
        np.testing.assert_allclose(ddot(A, B), C, rtol=1e-5)

    def test_sum2diag(self):
        A = self._random.randn(2, 2)
        B = sum2diag(A, 1.1)
        C = np.array([[ 0.30407302, -0.33062769],
                      [-1.22661901,  0.8317967 ]])
        np.testing.assert_allclose(B, C, rtol=1e-5)

if __name__ == '__main__':
    unittest.main()
