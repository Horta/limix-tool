import setuptools
from numpy.distutils.core import setup
import os
import sys

# BEFORE importing distutils, remove MANIFEST. distutils doesn't properly
# update it when the contents of directories change.
if os.path.exists('MANIFEST'): os.remove('MANIFEST')

def get_test_suite():
    from unittest import TestLoader
    return TestLoader().discover('limix_util')

def configuration(parent_package='', top_path=None):
    from numpy.distutils.misc_util import Configuration

    config = Configuration(None, parent_package, top_path)
    config.set_options(ignore_setup_xxx_py=True,
                       assume_default_configuration=True,
                       delegate_options_to_subpackages=True,
                       quiet=True)

    config.add_subpackage('limix_util')

    return config

def setup_package():
    src_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    old_path = os.getcwd()
    os.chdir(src_path)
    sys.path.insert(0, src_path)

    # build_requires = ['numpy', 'scipy', 'progressbar', 'humanfriendly',
    #                   'h5py']

    metadata = dict(
        name='limix-util',
        test_suite='setup.get_test_suite',
        # setup_requires=build_requires,
        # install_requires=build_requires,
        packages=['limix_util']
    )

    metadata['configuration'] = configuration

    try:
        setup(**metadata)
    finally:
        del sys.path[0]
        os.chdir(old_path)

if __name__ == '__main__':
    setup_package()
