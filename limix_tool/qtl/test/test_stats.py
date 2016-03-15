import unittest
import numpy as np
from limix_tool.qtl.stats import hwe_test
from limix_tool.qtl.stats import hwe_stat

class TestStats(unittest.TestCase):
    def test_hwe_test_odd(self):
        N = 100
        n_a = 21
        n_b = 2*N - n_a
        pv = []
        n_abs = range(1, n_a+2, 2)
        for n_ab in n_abs:
            n_b = (N - (n_a-n_ab)/2 - n_ab) * 2 + n_ab
            pv.append(hwe_stat(n_ab, n_a, n_b))

        pv_ideal = [2.2528461190398889e-13, 1.3389415434160398e-10,
                    2.1307043119526107e-08, 1.4247843459546118e-06,
                    4.8363303029661291e-05, 0.00091885946770931307,
                    0.010293433548874778, 0.069576454405006927,
                    0.28404150044336751, 1.0, 0.59364517592731658]
        np.testing.assert_almost_equal(pv_ideal, pv)

    def test_hwe_test_even(self):
        N = 100
        n_a = 20
        n_b = 2*N - n_a
        pv = []
        n_abs = range(0, n_a+2, 2)
        for n_ab in n_abs:
            n_b = (N - (n_a-n_ab)/2 - n_ab) * 2 + n_ab
            pv.append(hwe_stat(n_ab, n_a, n_b))

        pv_ideal = [1.0727838662094675e-14, 1.9320837430432614e-11,
                    5.175120098433163e-09, 4.8913281073122185e-07,
                    2.1541292353257525e-05, 0.00050433748452852699,
                    0.0067221672322403288, 0.052638448446112096,
                    0.24319101548367975, 1.0, 0.59149515040312262]
        np.testing.assert_almost_equal(pv_ideal, pv)

    def test_hwe_test_matrix(self):
        np.random.seed(938)
        X = np.random.randint(0, 3, (100, 5))
        pv_ideal = [2.75231965e-03, 6.45057302e-06, 7.81174620e-07,
                    1.51675348e-02, 2.22026154e-06]
        pv = hwe_test(X.T)
        np.testing.assert_almost_equal(pv_ideal, pv)

if __name__ == '__main__':
    unittest.main()
