from functools import partial
from twisted.internet.threads import deferToThreadPool

class Thimble(object):
    """A Twisted thread-pool wrapper for a blocking API.

    """
    def __init__(self, reactor, pool, wrapped, blocking_methods):
        self._reactor = reactor
        self._pool = pool
        self._wrapped = wrapped
        self._blocking_methods = blocking_methods


    def _deferToThreadPool(self, f, *args, **kwargs):
        """Defers execution of ``f(*args, **kwargs)`` to the thread pool.

        This returns a deferred which will callback with the result of
        that expression, or errback with a failure wrapping the raised
        exception.

        """
        return deferToThreadPool(self._reactor, self._pool, f, *args, **kwargs)


    def __getattr__(self, attr):
        """Gets an attribute from the wrapped object, wrapping it to make it
        asynchronous if necessary.

        """
        value = getattr(self._wrapped, attr)

        if attr in self._blocking_methods:
            value = partial(self._deferToThreadPool, value)

        return value
