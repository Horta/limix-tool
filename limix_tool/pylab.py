import limix_plot.pylab as plt
from .qqplot import QQPlot

if __name__ == '__main__':
    import numpy as np
    random = np.random.RandomState(9823)
    qq = QQPlot(plt.gca())
    N = 500
    qq.add(random.rand(N), 'label1')
    qq.add(random.rand(N), 'label2')
    qq.add(random.rand(N), 'label3')
    qq.add(random.rand(N), 'label4')
    qq.plot(confidence=True)
    plt.show()
