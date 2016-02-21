import os
if os.path.exists('MANIFEST'): os.remove('MANIFEST')
import sys
import imp
import textwrap

try:
    imp.find_module('numpy')
except ImportError:
    print('Fatal: could not import numpy. Please, make sure it is installed.')
    sys.exit(1)

MAJOR               = 0
MINOR               = 1
MICRO               = 28
ISRELEASED          = True
VERSION             = '%d.%d.%d' % (MAJOR, MINOR, MICRO)

if sys.version_info[0] >= 3:
    import builtins
else:
    import __builtin__ as builtins

# This is a bit hackish: we are setting a global variable so that the main
# limix-util __init__ can detect if it is being loaded by the setup routine, to
# avoid attempting to load components that aren't built yet.  While ugly, it's
# a lot more robust than what was previously being used.
builtins.__LIMIX_UTIL_SETUP__ = True

def parse_setuppy_commands():
    """Check the commands and respond appropriately.  Disable broken commands.
    Return a boolean value for whether or not to run the build or not (avoid
    parsing Cython and template files if False).
    """
    if len(sys.argv) < 2:
        # User forgot to give an argument probably, let setuptools handle that.
        return True

    info_commands = ['--help-commands', '--name', '--version', '-V',
         '--fullname', '--author', '--author-email',
         '--maintainer', '--maintainer-email', '--contact',
         '--contact-email', '--url', '--license', '--description',
         '--long-description', '--platforms', '--classifiers',
         '--keywords', '--provides', '--requires', '--obsoletes']
    # Add commands that do more than print info, but also don't need Cython and
    # template parsing.
    info_commands.extend(['egg_info', 'install_egg_info', 'rotate'])

    for command in info_commands:
        if command in sys.argv[1:]:
            return False

    good_commands = ('develop', 'sdist', 'build', 'build_ext', 'build_py',
                 'build_clib', 'build_scripts', 'bdist_wheel', 'bdist_rpm',
                 'bdist_wininst', 'bdist_msi', 'bdist_mpkg')

    for command in good_commands:
        if command in sys.argv[1:]:
            return True

    # The following commands are supported, but we need to show more
    # useful messages to the user
    if 'install' in sys.argv[1:]:
        print(textwrap.dedent("""
            Note: if you need reliable uninstall behavior, then install
            with pip instead of using `setup.py install`:
              - `pip install .`       (from a git repo or downloaded source
                                       release)
              - `pip install limix-util`   (last Limix-util release on PyPi)
            """))
        return True

    if '--help' in sys.argv[1:] or '-h' in sys.argv[1]:
        print(textwrap.dedent("""
        Limix-util-specific help
        -------------------
        To install Limix-util from here with reliable uninstall, we recommend
        that you use `pip install .`. To install the latest Limix-util release
        from PyPi, use `pip install limix-util`.
        Setuptools commands help
        ------------------------
        """))
        return False

        # The following commands aren't supported.  They can only be executed when
    # the user explicitly adds a --force command-line argument.
    bad_commands = dict(
        test="""
            `setup.py test` is not supported.  Use one of the following
            instead:
              - `python runtests.py`              (to build and test)
              - `python runtests.py --no-build`   (to test installed numpy)
              - `>>> numpy.test()`           (run tests for installed numpy
                                              from within an interpreter)
            """,
        upload="""
            `setup.py upload` is not supported, because it's insecure.
            Instead, build what you want to upload and upload those files
            with `twine upload -s <filenames>` instead.
            """,
        upload_docs="`setup.py upload_docs` is not supported",
        easy_install="`setup.py easy_install` is not supported",
        clean="""
            `setup.py clean` is not supported, use one of the following instead:
              - `git clean -xdf` (cleans all files)
              - `git clean -Xdf` (cleans all versioned files, doesn't touch
                                  files that aren't checked into the git repo)
            """,
        check="`setup.py check` is not supported",
        register="`setup.py register` is not supported",
        bdist_dumb="`setup.py bdist_dumb` is not supported",
        bdist="`setup.py bdist` is not supported",
        build_sphinx="""
            `setup.py build_sphinx` is not supported, use the
            Makefile under doc/""",
        flake8="`setup.py flake8` is not supported, use flake8 standalone",
        )
    bad_commands['nosetests'] = bad_commands['test']
    for command in ('upload_docs', 'easy_install', 'bdist', 'bdist_dumb',
                     'register', 'check', 'install_data', 'install_headers',
                     'install_lib', 'install_scripts', ):
        bad_commands[command] = "`setup.py %s` is not supported" % command

    for command in bad_commands.keys():
        if command in sys.argv[1:]:
            print(textwrap.dedent(bad_commands[command]) +
                  "\nAdd `--force` to your command to use it anyway if you "
                  "must (unsupported).\n")
            sys.exit(1)

    # If we got here, we didn't detect what setup.py command was given
    import warnings
    warnings.warn("Unrecognized setuptools command, proceeding with "
                  "generating Cython sources and expanding templates")
    return True


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
    get_version_info = mod.get_version_info
    generate_cython = mod.generate_cython

    src_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    old_path = os.getcwd()
    os.chdir(src_path)
    sys.path.insert(0, src_path)

    # Rewrite the version file everytime
    filename = os.path.join(dirname, 'limix_util', 'version.py')
    write_version_py(VERSION, ISRELEASED, filename=filename)

    install_requires = ['progressbar', 'humanfriendly', 'numba']

    metadata = dict(
        name='limix-util',
        maintainer = "Limix Developers",
        maintainer_email = "horta@ebi.ac.uk",
        test_suite='setup.get_test_suite',
        packages=['limix_util'],
        install_requires=install_requires
    )

    run_build = parse_setuppy_commands()

    from setuptools import setup

    if run_build:
        generate_cython(['limix_util/plink_'])
        from numpy.distutils.core import setup
        metadata['configuration'] = configuration
    else:
        # Version number is added to metadata inside configuration() if build
        # is run.
        metadata['version'] = get_version_info(VERSION, ISRELEASED,
                                               filename=filename)[0]

    try:
        setup(**metadata)
    finally:
        del sys.path[0]
        os.chdir(old_path)

if __name__ == '__main__':
    setup_package()
