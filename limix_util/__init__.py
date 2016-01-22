import path_
import pickle_
import time_
import str_
import hdf5_
from misc import traverse_dict
from misc import ring
from misc import BeginEnd
from misc import group_by
from progress import ProgressBar
import cached

def isfloat(value):
    try:
        float(value)
        return True
    except ValueError:
        return False
