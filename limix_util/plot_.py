from __future__ import division
import matplotlib.pylab as plt
from numpy import asarray, asscalar
import os

def show(fig=None, dst_fp=None):
    import path_

    fig = plt.gcf() if fig is None else fig

    if dst_fp is None:
        with path_.temp_folder() as folder:
            fout = os.path.join(folder, 'tmp.png')
            fig.savefig(fout)
            os.system("imgcat " + fout)
    else:
        fig.savefig(dst_fp)
        os.system("imgcat " + dst_fp)

    plt.close()

def heatmap(X, ax=None, show=True):
    ax = plt.gca() if ax is None else ax

    im = ax.imshow(X)
    plt.colorbar(im, ax=ax)

    ax.set_frame_on(False)
    ax.grid(False)

    if show:
        import limix_util as lu
        lu.plot_.show()

class BarPlotBase(object):
    def __init__(self):
        self._values = dict()
        self._colors = dict()

    @property
    def _labels(self):
        labels = set()
        for v in self._values.values():
            labels = labels.union(v.keys())
        return sorted(list(labels))

    @property
    def _group_labels(self):
        return sorted(self._values.keys())

    def _get_color(self, label):
        return self._colors[label]

    def _get_values(self, grp):
        vs = self._values[grp].values()
        ks = self._values[grp].keys()
        return [x for (y, x) in sorted(zip(ks,vs))]

    def set_color(self, label, color):
        self._colors[label] = color

    def add(self, point, err, label, grp=''):
        raise NotImplementedError

    def plot(self, ax=None):
        raise NotImplementedError

class ErrBarPlot(BarPlotBase):
    def __init__(self):
        super(ErrBarPlot, self).__init__()

    def add(self, point, err, label, grp=''):
        if grp not in self._values:
            self._values[grp] = dict()
        self._values[grp][label] = dict()
        self._values[grp][label]['point'] = asscalar(point)
        self._values[grp][label]['err'] = asscalar(err)

    def plot(self, ax=None):
        ax = plt.gca() if ax is None else ax

        width = 4./5.
        pos = []
        left = 0
        y = []
        yerr = []
        colors = []

        for grp_label in self._group_labels:
            v = self._get_values(grp_label)
            right = left + len(v)
            pos += range(left, right)
            left = right + 1
            y.extend([vi['point'] for vi in v])
            yerr.extend([vi['err'] for vi in v])
            colors.extend([self._get_color(l) for l in self._labels])

        pos = [p+1 for p in pos]

        bar = ax.bar(pos, y, width=width, yerr=yerr, color=colors)

        ngroups = len(self._values)
        width_bar = 1/(len(y) + ngroups - 1)
        width_group = (1 - (ngroups-1) * width_bar) / ngroups
        for i in xrange(ngroups):
            left = i * (width_group + width_bar)
            center = left + width_group/2
            ax.text(center, -0.03, self._group_labels[i],
                    transform=ax.transAxes, horizontalalignment='center',
                    verticalalignment='top', fontsize=15)

        ax.set_xticklabels([''] * len(ax.get_xticklabels()))
        ax.set_xlim([pos[0] - 0.2, pos[-1] + 1.])

        return ax

class FillBarPlot(BarPlotBase):
    def __init__(self):
        super(FillBarPlot, self).__init__()

    def add(self, total, level, label, grp=''):
        if grp not in self._values:
            self._values[grp] = dict()
        self._values[grp][label] = dict()
        self._values[grp][label]['total'] = asscalar(total)
        self._values[grp][label]['level'] = asscalar(level)

    def plot(self, ax=None):
        ax = plt.gca() if ax is None else ax

        width = 4./5.
        pos = []
        left = 0
        total = []
        level = []
        colors = []

        for grp_label in self._group_labels:
            v = self._get_values(grp_label)
            right = left + len(v)
            pos += range(left, right)
            left = right + 1
            total.extend([vi['total'] for vi in v])
            level.extend([vi['level'] for vi in v])
            colors.extend([self._get_color(l) for l in self._labels])

        pos = [p+1 for p in pos]

        ax.bar(pos, total, width=width, color=['white']*len(colors),
               edgecolor=['black']*len(colors))
        ax.bar(pos, level, width=width, color=colors)

        ngroups = len(self._values)
        width_bar = 1/(len(total) + ngroups - 1)
        width_group = (1 - (ngroups-1) * width_bar) / ngroups
        for i in xrange(ngroups):
            left = i * (width_group + width_bar)
            center = left + width_group/2
            ax.text(center, -0.03, self._group_labels[i],
                    transform=ax.transAxes, horizontalalignment='center',
                    verticalalignment='top', fontsize=15)

        ax.set_xticklabels([''] * len(ax.get_xticklabels()))
        ax.set_xlim([pos[0] - 0.2, pos[-1] + 1.])

        return ax


class BoxPlot(object):
    def __init__(self):
        self._values = dict()
        self._colors = dict()

    @property
    def _labels(self):
        labels = set()
        for v in self._values.values():
            labels = labels.union(v.keys())
        return sorted(list(labels))

    @property
    def _group_labels(self):
        return sorted(self._values.keys())

    def _get_color(self, label):
        return self._colors[label]

    def _get_values(self, grp):
        vs = self._values[grp].values()
        ks = self._values[grp].keys()
        return [x for (y, x) in sorted(zip(ks,vs))]

    def set_color(self, label, color):
        self._colors[label] = color

    def add(self, values, label, grp=''):
        if grp not in self._values:
            self._values[grp] = dict()
        self._values[grp][label] = asarray(values).ravel()

    def plot(self, ax=None):
        ax = plt.gca() if ax is None else ax

        pos = []
        left = 0
        data = []
        colors = []

        for grp_label in self._group_labels:
            v = self._get_values(grp_label)
            right = left + len(v)
            pos += range(left, right)
            left = right + 1
            data.extend(v)
            colors.extend([self._get_color(l) for l in self._labels])

        pos = [p+1 for p in pos]

        bp = ax.boxplot(data, notch=False, patch_artist=True, positions=pos)

        for i in xrange(len(colors)):
            c = colors[i]
            plt.setp(bp['boxes'][i], color=c, facecolor=c)
        plt.setp(bp['whiskers'], color='black')
        plt.setp(bp['fliers'], color='red', marker='+')

        fakes = []
        for l in self._labels:
            fake, = ax.plot([1,1], color=self._get_color(l))
            fakes.append(fake)

        labels = self._labels
        ax.legend(fakes, labels, bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
                ncol=len(labels), mode="expand", borderaxespad=0.)

        for fake in fakes:
            fake.set_visible(False)

        ngroups = len(self._values)
        width_bar = 1/(len(data) + ngroups - 1)
        width_group = (1 - (ngroups-1) * width_bar) / ngroups
        for i in xrange(ngroups):
            left = i * (width_group + width_bar)
            center = left + width_group/2
            ax.text(center, -0.03, self._group_labels[i], transform=ax.transAxes,
                    horizontalalignment='center', verticalalignment='top',
                    fontsize=15)

        ax.set_xticklabels([''] * len(ax.get_xticklabels()))

        return ax

if __name__ == '__main__':
    import numpy as np
    X = np.random.randn(1000,1000)
    heatmap(X)
    show()
