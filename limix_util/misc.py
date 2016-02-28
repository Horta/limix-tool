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
