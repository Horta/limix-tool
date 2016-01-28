import matplotlib.pylab as plt
import os

def show(fig=None):
    import path_

    fig = plt.gcf() if fig is None else fig

    with path_.temp_folder() as folder:
        fout = os.path.join(folder, 'tmp.png')
        fig.savefig(fout)
        os.system("imgcat " + fout)

def heatmap(X, ax=None):
    ax = plt.gca() if ax is None else ax

    im = ax.imshow(X)
    plt.colorbar(im, ax=ax)

    ax.set_frame_on(False)
    ax.grid(False)

if __name__ == '__main__':
    import numpy as np
    X = np.random.randn(1000,1000)
    heatmap(X)
    show()
