from sys import platform as _platform

def platform():
    if _platform == "linux" or _platform == "linux2":
        return 'linux'
    elif _platform == "darwin":
        return 'osx'
    elif _platform == "win32":
        return 'win'
    return 'unknown'
