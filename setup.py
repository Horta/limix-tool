import os
if os.path.exists('MANIFEST'): os.remove('MANIFEST')
import setuptools
from setuptools import setup
from numpy.distutils.core import setup
import sys
import imp

MAJOR               = 0
MINOR               = 1
MICRO               = 1
ISRELEASED          = True
VERSION             = '%d.%d.%d' % (MAJOR, MINOR, MICRO)


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

    config.get_version('limix_util/version.py') # sets config.version

    return config

def setup_package():
    path = os.path.realpath(__file__)
    dirname = os.path.dirname(path)
    mod = imp.load_source('__init__',
                          os.path.join(dirname, 'build_util', '__init__.py'))
    write_version_py = mod.write_version_py
    # generate_cython = mod.generate_cython

    src_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    old_path = os.getcwd()
    os.chdir(src_path)
    sys.path.insert(0, src_path)

    # Rewrite the version file everytime
    write_version_py(VERSION, ISRELEASED, filename='limix_util/version.py')

    build_requires = ['numpy', 'setuptools']
    install_requires = build_requires + ['scipy', 'progressbar',
                                         'humanfriendly', 'h5py']

    metadata = dict(
        name='limix-util',
        maintainer = "Limix Developers",
        maintainer_email = "horta@ebi.ac.uk",
        test_suite='setup.get_test_suite',
        setup_requires=build_requires,
        install_requires=install_requires,
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
