from functools import partial
from twisted.internet.threads import deferToThreadPool

class Thimble(object):
    def __init__(self, reactor, pool, wrapped, blocking_methods):
        self._reactor = reactor
        self._pool = pool
        self._wrapped = wrapped
        self._blocking_methods = blocking_methods


    def _deferToThreadPool(self, f, *args, **kwargs):
        return deferToThreadPool(self._reactor, self._pool, f, *args, **kwargs)


    def __getattr__(self, attr):
        value = getattr(self._wrapped, attr)

        if attr in self._blocking_methods:
            value = partial(self._deferToThreadPool, value)

        return value
