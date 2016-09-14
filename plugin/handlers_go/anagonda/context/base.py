
# Copyright (C) 2013 - 2016 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

import os
import sys
import shlex
from subprocess import PIPE

from process import spawn

from .error import AnaGondaError, GoGetError


class AnaGondaContext(object):
    """Every anaGonda context must inherit from this class
    """

    def __init__(self, env_ctx, go_get_url):
        self.__go_get_url = go_get_url
        self.__env = env_ctx

    def __enter__(self):
        """Check binary existence or run go get
        """

        if self._bin_found is None:
            if not os.path.exists(self.binary):
                try:
                    self.go_get()
                except AnaGondaError:
                    self._bin_found = False
                    raise

    def __exit__(self, *ext):
        """Do nothing
        """

    @property
    def go(self):
        """Return the Go binary for this GOROOT
        """

        if self.__env.goroot == "":
            return "go"  # pray for it being in the PATH

        return os.path.join(self.__env.goroot, 'bin', 'go')

    @property
    def env(self):
        """Prepare the environ with go vars and sanitization
        """

        env = {}
        curenv = os.enviton.copy()
        for key in curenv:
            env[str(key)] = str(curenv[key])

        env['GOPATH'] = self.__env.gopath
        env['GOROOT'] = self.__env.goroot
        env['CGO_ENABLED'] = self.__env.cgo_enabled
        return env

    def go_get(self):
        """Go get the code to execute the scoped context
        """

        args = shlex.split('{0} get {1}'.format(
            self.go, self.__go_get_url), posix=os.name != 'nt')
        go = spawn(args, stdout=PIPE, stderr=PIPE, env=self.env)
        out, err = go.communicate()
        if err is not None and len(err) > 0:
            if sys.version_info >= (3, 0):
                err = err.decode('utf8')
            raise GoGetError(err)
        self._bin__found = True