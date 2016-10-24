import unittest
import numpy as np
from limix_tool.qtl.score import WindowScore
import scipy.stats as stats

class TestScore(unittest.TestCase):
    def test_window_score(self):
        random = np.random.RandomState(4875)
        n = 100
        p = 500
        ws = WindowScore()
        pos = np.sort(random.choice(1000000, n, replace=False))
        X = random.randint(0, 3, size=(n, p))

        causals = [4, 51]

        r2s = []
        for c in causals:
            r2 = []
            cx = X[:,c]
            for ox in X.T:
                slope, intercept, r_value, p_value, std_err = stats.linregress(cx, ox)
                r2.append(r_value**2)
            r2s.append(r2)

        r2s = np.asarray(r2s, float)
        r2s += 0.49
        r2s = np.clip(r2s, 0, 1)
        ws.set_chrom(22, pos, causals)
        pv = random.rand(n)
        cm = ws.confusion(pv)
        ideal = [0.0947368421, 0.0937500000]

        np.testing.assert_array_almost_equal(ideal, cm.precision[95:97])
        self.assertAlmostEqual(cm.recall[31], 0.111111111111)

    def test_window_score_X(self):
        random = np.random.RandomState(4875)
        n = 100
        p = 500
        ws = WindowScore()
        # pos = np.sort(random.choice(1000000, n, replace=False))
        pos = np.sort(random.choice(1000000, p, replace=False))
        X = random.randint(0, 3, size=(n, p))

        causals = [4, 51]

        ws.set_chrom(22, pos, causals, X=X)
        pv = random.rand(p)
        cm = ws.confusion(pv)
        ideal = [0.0947368421, 0.0937500000]

        np.testing.assert_array_equal(cm.recall[0], 0)
        np.testing.assert_array_equal(cm.recall[-1], 1)
        np.testing.assert_equal(np.isnan(cm.precision[0]), True)
        np.testing.assert_allclose(cm.precision[95], 0.0105263157895)


if __name__ == '__main__':
    unittest.main()
