from __future__ import division, print_function
import os
import sys
from setuptools import setup, find_packages
from setuptools.extension import Extension
from Cython.Build import cythonize
from Cython.Distutils import build_ext

PKG_NAME = 'limix_tool'
VERSION = '0.1.16'

try:
    from distutils.command.bdist_conda import CondaDistribution
except ImportError:
    conda_present = False
else:
    conda_present = True

try:
    import numpy as np
except ImportError:
    print("Error: numpy package couldn't be found." +
          " Please, install it so I can proceed.")
    sys.exit(1)
else:
    print("Good: numpy %s" % np.__version__)

try:
    import scipy
except ImportError:
    print("Error: scipy package couldn't be found." +
          " Please, install it so I can proceed.")
    sys.exit(1)
else:
    print("Good: scipy %s" % scipy.__version__)

try:
    import cython
except ImportError:
    print("Error: cython package couldn't be found." +
          " Please, install it so I can proceed.")
    sys.exit(1)
else:
    print("Good: cython %s" % cython.__version__)

try:
    import numba
except ImportError:
    print("Error: numba package couldn't be found." +
          " Please, install it so I can proceed.")
    sys.exit(1)
else:
    print("Good: numba %s" % numba.__version__)


def plink_extension():
    curdir = os.path.abspath(os.path.dirname(__file__))

    plink_folder = os.path.join(curdir, 'limix_tool/plink_/')

    src = ['write.pyx']
    src = [os.path.join(plink_folder, s) for s in src]

    hdr = ['write.pxd']
    hdr = [os.path.join(plink_folder, h) for h in hdr]

    depends = src + hdr

    ext = Extension('limix_tool/plink_/write', src,
                    include_dirs=[np.get_include()], depends=depends)

    return ext


def get_test_suite():
    import logging
    from unittest import TestLoader
    logging.basicConfig(level=logging.WARN)
    return TestLoader().discover(PKG_NAME)


def setup_package():
    src_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    old_path = os.getcwd()
    os.chdir(src_path)
    sys.path.insert(0, src_path)

    install_requires = ['hcache', 'limix_math', 'limix_util', 'colour']
    setup_requires = []

    metadata = dict(
        name=PKG_NAME,
        maintainer="Limix Developers",
        version=VERSION,
        maintainer_email="horta@ebi.ac.uk",
        test_suite='setup.get_test_suite',
        packages=find_packages(),
        license="BSD",
        url='http://pmbio.github.io/limix/',
        install_requires=install_requires,
        setup_requires=setup_requires,
        zip_safe=False,
        ext_modules=cythonize([plink_extension()]),
        cmdclass=dict(build_ext=build_ext)
    )

    if conda_present:
        metadata['distclass'] = CondaDistribution
        metadata['conda_buildnum'] = 1
        metadata['conda_features'] = ['mkl']

    try:
        setup(**metadata)
    finally:
        del sys.path[0]
        os.chdir(old_path)

if __name__ == '__main__':
    setup_package()
