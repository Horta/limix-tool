import contextlib
import errno
import tempfile
import shutil
import os
import subprocess
import sys

@contextlib.contextmanager
def temp_folder():
    folder = tempfile.mkdtemp()
    try:
        yield folder
    finally:
        shutil.rmtree(folder)

def count_lines(filepath):
    return sum(1 for line in open(filepath, 'r'))

class ChDir(object):
    """
    Step into a directory temporarily.
    """
    def __init__(self, path):
        self.old_dir = os.getcwd()
        self.new_dir = path

    def __enter__(self):
        os.chdir(self.new_dir)

    def __exit__(self, *args):
        os.chdir(self.old_dir)

def make_sure_path_exists(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno != errno.EEXIST:
            raise

def cp(folder_src, folder_dst):
    retcode = subprocess.call("cp " + folder_src + "/* " + folder_dst,
                              shell=True)

    if retcode < 0:
        print >>sys.stderr, "Child was terminated by signal", -retcode

def rrm(paths):
    paths = paths if isinstance(paths, list) else [paths]
    if len(paths) == 0:
        return

    cmd = subprocess.list2cmdline(['rm', '-rf'] + paths)
    retcode = subprocess.call(cmd, shell=True)

    if retcode < 0:
        print >>sys.stderr, "Child was terminated by signal", -retcode

def touch(fname, times=None):
    with open(fname, 'a'):
        os.utime(fname, times)
