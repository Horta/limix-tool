import matplotlib.pylab as plt
import os

def show(fig=None):
    import path_

    fig = plt.gcf() if fig is None else fig

    with path_.temp_folder() as folder:
        fout = os.path.join(folder, 'tmp.png')
        fig.savefig(fout)
        os.system("imgcat " + fout)
