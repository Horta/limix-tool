import os
import sys
from setuptools import setup
from setuptools import find_packages


def setup_package():
    src_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    old_path = os.getcwd()
    os.chdir(src_path)
    sys.path.insert(0, src_path)

    needs_pytest = {'pytest', 'test', 'ptr'}.intersection(sys.argv)
    pytest_runner = ['pytest-runner'] if needs_pytest else []

    setup_requires = [] + pytest_runner
    install_requires = ['pytest', 'hcache>=1.0', 'limix_math>=1.0.1',
                        'limix_util>=1.0', 'colour', 'limix_plot>=1.0.1']
    tests_require = install_requires

    metadata = dict(
        name='limix_tool',
        version='1.0.0',
        maintainer="Limix Developers",
        maintainer_email="horta@ebi.ac.uk",
        license="MIT",
        url='http://github.com/Horta/limix-tool',
        packages=find_packages(),
        zip_safe=True,
        install_requires=install_requires,
        setup_requires=setup_requires,
        tests_require=tests_require,
        include_package_data=True,
        classifiers=[
            "Development Status :: 5 - Production/Stable",
            "License :: OSI Approved :: MIT License",
            "Programming Language :: Python :: 2.7",
            "Programming Language :: Python :: 3.4",
            "Programming Language :: Python :: 3.5",
            "Operating System :: OS Independent",
        ],
    )

    try:
        from distutils.command.bdist_conda import CondaDistribution
    except ImportError:
        pass
    else:
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
