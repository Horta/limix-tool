# We first need to detect if we're being called as part of the limix-util setup
# procedure itself in a reliable manner.
try:
    __LIMIX_UTIL_SETUP__
except NameError:
    __LIMIX_UTIL_SETUP__ = False

if not __LIMIX_UTIL_SETUP__:
    import path_
    import pickle_
    import time_
    import str_
    import hdf5_
    import data_
    import plot_
    import inspect_
    import array_
    import h2
    import data_format
    from misc import traverse_dict
    from misc import ring
    from misc import BeginEnd
    from misc import group_by
    import system_
    from progress import ProgressBar
    import cached

    def isfloat(value):
        try:
            float(value)
            return True
        except ValueError:
            return False
