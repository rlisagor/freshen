#-*- coding: utf8 -*-

from os.path import abspath, commonprefix, sep, pardir, join
import os
curdir = os.getcwd()

def relpath(path, start=curdir):
    """Return a relative version of a path"""

    if not path:
        raise ValueError("no path specified")

    start_list = abspath(start).split(sep)
    path_list = abspath(path).split(sep)

    # Work out how much of the filepath is shared by start and path.
    i = len(commonprefix([start_list, path_list]))

    rel_list = [pardir] * (len(start_list)-i) + path_list[i:]
    if not rel_list:
        return curdir
    return join(*rel_list)

    
if __name__ == "__main__":
    print relpath("/tmp/dir1/file", "/tmp")
    print relpath("/tmp/dir1/file", "/usr")
