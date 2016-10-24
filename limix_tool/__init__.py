from pkg_resources import get_distribution
from pkg_resources import DistributionNotFound

try:
    __version__ = get_distribution('limix-tool').version
except DistributionNotFound:
    __version__ = 'unknown'

def test():
    import os
    p = __import__('limix_tool').__path__[0]
    src_path = os.path.abspath(p)
    old_path = os.getcwd()
    os.chdir(src_path)

    try:
        return_code = __import__('pytest').main(['-q'])
    finally:
        os.chdir(old_path)

    if return_code == 0:
        print("Congratulations. All tests have passed!")

    return return_code
