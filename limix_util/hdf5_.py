import h5py
import numpy as np

def tree(f_or_filepath, root_name='/', ret=False):
    if isinstance(f_or_filepath, str):
        with h5py.File(f_or_filepath) as f:
            _tree(f, root_name, ret)
    else:
        _tree(f_or_filepath, root_name, ret)

def _tree(f, root_name='/', ret=False):
    import asciitree

    _names = []
    def get_names(name, obj):
        if isinstance(obj, h5py._hl.dataset.Dataset):
            dtype = str(obj.dtype)
            shape = str(obj.shape)
            _names.append("%s [%s, %s]" % (name, dtype, shape))
        else:
            _names.append(name)

    f.visititems(get_names)
    class Node(object):
        def __init__(self, name, children):
            self.name = name
            self.children = children

        def __str__(self):
            return self.name
    root = Node(root_name, dict())

    def add_to_node(node, ns):
        if len(ns) == 0:
            return
        if ns[0] not in node.children:
            node.children[ns[0]] = Node(ns[0], dict())
        add_to_node(node.children[ns[0]], ns[1:])

    _names = sorted(_names)
    for n in _names:
        ns = n.split('/')
        add_to_node(root, ns)

    def child_iter(node):
        keys = node.children.keys()
        indices = np.argsort(keys)
        indices = np.asarray(indices)
        return list(np.asarray(node.children.values())[indices])

    msg = asciitree.draw_tree(root, child_iter)
    if ret:
        return msg
    print msg
