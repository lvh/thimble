"""Implementation of a Twisted-friendly thread pool wrapper."""
from functools import partial
from twisted.internet.threads import deferToThreadPool
from twisted.internet.defer import fail
from twisted.internet.error import ReactorNotRunning


class Thimble(object):

    """A Twisted thread-pool wrapper for a blocking API."""

    def __init__(self, reactor, pool, wrapped, blocking_methods,
                 attr_hooks=None):
        """Initialize a :class:`Thimble`.

        :param reactor: The reactor that will handle events.
        :type reactor: :class:`twisted.internet.interfaces.IReactorThreads` and
            :class:`twisted.internet.interfaces.IReactorCore`. Pretty much any
            real reactor implementation will do.
        :param pool: The thread pool to defer to.
        :type pool: :class:`twisted.python.threadpool.ThreadPool`
        :param wrapped: The blocking implementation being wrapped.
        :param blocking_methods: The names of the methods that will be wrapped
            and executed in the thread pool.
        :type blocking_methods: ``list`` of native ``str``
        :param attr_hooks: A mapping of attribute names to attribute hook
            functions. Attribute hook functions will be called with this
            thimble object, the attribute name being accessed, and the
            current attribute value; their return value will be used in
            place of the real attribute value.
        :type attr_hooks: :class:`dict` of native :class:`str` to ternary
            callables
        """
        self._reactor = reactor
        self._pool = pool
        self._wrapped = wrapped
        self._blocking_methods = blocking_methods
        self._attr_hooks = attr_hooks if attr_hooks is not None else {}

    def _deferToThreadPool(self, f, *args, **kwargs):
        """Defer execution of ``f(*args, **kwargs)`` to the thread pool.

        This returns a deferred which will callback with the result of
        that expression, or errback with a failure wrapping the raised
        exception.

        """
        if self._pool.joined:
            return fail(
                ReactorNotRunning("This thimble's threadpool already stopped.")
            )
        if not self._pool.started:
            self._pool.start()
            self._reactor.addSystemEventTrigger(
                'during', 'shutdown', self._pool.stop)

        return deferToThreadPool(self._reactor, self._pool, f, *args, **kwargs)

    def __getattr__(self, attr):
        """Get and maybe wraps an attribute from the wrapped object.

        If the attribute is blocking, it will be wrapped so that
        calling it will return a Deferred and the actual function will
        be ran in a thread pool.

        """
        value = getattr(self._wrapped, attr)

        hook = self._attr_hooks.get(attr)
        if hook is not None:
            value = hook(self, attr, value)

        if attr in self._blocking_methods:
            value = partial(self._deferToThreadPool, value)

        return value
