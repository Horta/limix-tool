from __future__ import division, print_function

try:
    import limix_build
except ImportError:
    import sys
    from ez_build import use_limix_build
    use_limix_build()
    import limix_build

import os
import sys
from setuptools import setup

if sys.version_info[0] >= 3:
    import builtins
else:
    import __builtin__ as builtins

builtins.__LIMIX_UTIL_SETUP__ = True

PKG_NAME            = "limix_util"
MAJOR               = 0
MINOR               = 0
MICRO               = 2
ISRELEASED          = True
VERSION             = '%d.%d.%d' % (MAJOR, MINOR, MICRO)

from limix_build import write_version_py
from limix_build.cythonize import cythonize
from limix_build import get_version_info

def get_test_suite():
    from unittest import TestLoader
    return TestLoader().discover(PKG_NAME)

def setup_package():
    src_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    old_path = os.getcwd()
    os.chdir(src_path)
    sys.path.insert(0, src_path)

    write_version_py(PKG_NAME, VERSION, ISRELEASED)

    install_requires = ['numba', 'humanfriendly', 'progressbar']
    try:
        import scipy
    except ImportError:
        install_requires.append('scipy')
    try:
        import h5py
    except ImportError:
        install_requires.append('h5py')
    try:
        import matplotlib
    except ImportError:
        install_requires.append('matplotlib')

    setup_requires = []
    try:
        import cython
    except ImportError:
        setup_requires.append('cython')

    metadata = dict(
        name=PKG_NAME,
        version=get_version_info(PKG_NAME, VERSION, ISRELEASED)[0],
        maintainer="Limix Developers",
        maintainer_email = "horta@ebi.ac.uk",
        license="BSD",
        url='http://pmbio.github.io/limix/',
        test_suite='setup.get_test_suite',
        packages=[PKG_NAME],
        install_requires=install_requires,
        setup_requires=setup_requires,
        zip_safe=False
    )

    cythonize(PKG_NAME)

    try:
        setup(**metadata)
    finally:
        del sys.path[0]
        os.chdir(old_path)

if __name__ == '__main__':
    setup_package()
