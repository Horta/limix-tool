def see(f, root_name='/'):
    import numpy as np
    import asciitree

    _names = []
    def get_names(name, obj):
        _names.append(name)
        for key, val in obj.attrs.iteritems():
            print "    %s: %s" % (key, val)

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
    return asciitree.draw_tree(root, child_iter)
