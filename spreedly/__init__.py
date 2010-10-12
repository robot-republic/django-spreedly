# -*- coding: utf-8 -
#
# This file is part of gunicorn released under the MIT license. 
# See the NOTICE for more information.

import os

# Inspired by http://github.com/benoitc/gunicorn/blob/master/gunicorn/util.py
try:#python 2.6, use subprocess
    import subprocess
    subprocess.Popen  # trigger ImportError early
    closefds = os.name == 'posix'
    
    def popen3(cmd, mode='t', bufsize=0):
        p = subprocess.Popen(cmd, shell=True, bufsize=bufsize,
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
            close_fds=closefds)
        p.wait()
        return (p.stdin, p.stdout, p.stderr)
except ImportError:
    subprocess = None
    popen3 = os.popen3


if os.environ.get('release') != "true":

    minor_tag = ""
    try:

        stdin, stdout, stderr = popen3("git rev-parse --short HEAD --")
        error = stderr.read()
        if not error:
            git_tag = stdout.read()[:-1]
            minor_tag = ".%s-git" % git_tag
    except OSError:        
        pass
else:
    minor_tag = ""

version_info = (0, 1, "0%s" % minor_tag)
__version__ = ".".join(map(str, version_info))