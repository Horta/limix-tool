import math
import sys
import time
from collections import OrderedDict

def _fetch_all_group_values(olist, group_name):
    values = set()
    for o in olist:
        values.add(getattr(o, group_name))
    return list(values)

def group_by(olist, group_names, sort_key=None):
    if not isinstance(group_names, list):
        group_names = [group_names]

    if len(group_names) == 0:
        return olist

    group_name = group_names[0]
    vals = _fetch_all_group_values(olist, group_name)
    vals.sort(key=sort_key)
    grouped = OrderedDict([(v, []) for v in vals])

    for o in olist:
        v = getattr(o, group_name)
        grouped[v].append(o)

    for (k, tl) in grouped.iteritems():
        grouped[k] = group_by(tl, group_names[1:])

    return grouped

def traverse_dict(d, visit_func, opt=None):
    opts = visit_func(d, opt)
    if isinstance(d, dict):
        i = 0
        for v in d.itervalues():
            traverse_dict(v, visit_func, opts[i] if opts else None)
            i += 1

def ring():
    sys.stdout.write('\a')
    sys.stdout.flush()

class BeginEnd(object):
    def __init__(self, task, silent=False):
        self._task = str(task)
        self._start = None
        self._silent = silent

    def __enter__(self):
        self._start = time.time()
        if not self._silent:
            print('-- %s start --' % self._task)
            sys.stdout.flush()

    def __exit__(self, *args):
        elapsed = time.time() - self._start
        if not self._silent:
            print('-- %s end (%.2f s) --' % (self._task, elapsed))
            sys.stdout.flush()


if __name__ == '__main__':

    b = dict(group1=[3, 5, 2], group2=[5, 2], group3=[8])
    c = dict(group59=[1,2,3,4])

    a = dict(b=b, c=c)

    import matplotlib.gridspec as gridspec
    import pylab as plt

    def visit_func(d, opt):
        n = len(d)
        plot_this = n > 0 and not isinstance(d, dict)


        if plot_this:
            axis = plt.subplot(opt['ss'])
            axis.plot([1, 2, 3], [1, 2, 2])
            axis.set_xlabel(opt['title'])
        else:
            nrow = ncol = int(math.sqrt(n))
            if nrow * ncol < n:
                ncol += 1
            if nrow * ncol < n:
                nrow += 1

            grid = gridspec.GridSpecFromSubplotSpec(nrow, ncol,
                                         subplot_spec=opt['ss'])


            opts = []
            for i in xrange(len(d)):
                nopt = dict(title=d.keys()[i],
                            ss=grid[int(i / ncol), int(i % ncol)])
                opts.append(nopt)

            return opts

    ss = gridspec.GridSpec(1, 1)[0, 0]

    traverse_dict(a, visit_func, dict(title='root', ss=ss))

    import gwarped_exp as gwe
    gwe.plot.show_on_terminal()

def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = raw_input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")
