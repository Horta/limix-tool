from limix_plot.pylab import gcf, gca
from .qqplot import QQPlot

def qqplot(axes=None):
    if axes is None:
        axes = gca()

    return QQPlot(axes)
