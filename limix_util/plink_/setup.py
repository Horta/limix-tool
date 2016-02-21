import os
import sys
from numpy.distutils.misc_util import Configuration

curdir = os.path.abspath(os.path.dirname(__file__))

define_macros = []
if sys.platform == 'win32':
    define_macros.append(('_USE_MATH_DEFINES', None))

# cephes_src = join(curdir, 'cephes', '*.c')
# cephes_hdr = join(curdir, 'cephes', '*.h')

# cephes_src = glob.glob(cephes_src)
# cephes_hdr = glob.glob(cephes_hdr)

def configuration(parent_package='', top_path=None):

    config = Configuration('plink_', parent_package, top_path)

    config.add_extension('write_map', sources=['write_map.c'],
                         include_dirs=[curdir],
                         depends=['write_map.c']+\
                                 ['write_map.pyx', 'write_map.pxd'])

    # config.add_subpackage('test')
    config.add_define_macros(define_macros)
    config.make_config_py() # installs __config__.py
    return config

if __name__ == '__main__':
    print('This is the wrong setup.py file to run')
