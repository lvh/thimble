from twisted.trial.unittest import SynchronousTestCase
from thimble import Thimble
from thimble.test.util import FakeReactor, FakeThreadPool


class ExampleSynchronousThing(object):
    """An example thing with some blocking APIs which will be wrapped and
    some non-blocking (but still synchronous, i.e. non-Deferred returning)
    APIs that won't be.

    """
    @property
    def _wrapped(self):
        """This is here to verify that the ``_wrapped`` attribute of the
        :class:`Thimble` is used before the ``_wrapped`` attribute of
        the wrapped object.

        """
        return None

    @property
    def non_blocking_property(self):
        """A property that doesn't block. It is *synchronous*, it just doesn't
        block long enough to warrant wrapping it in a thread pool.

        """
        return 123

    def blocking_method(self, first, second):
        """A blocking method that adds two numbers.

        """
        return first + second

class _TestSetupMixin(object):
    def setUp(self):
        self.reactor = FakeReactor()
        self.pool = FakeThreadPool()
        self.wrapped = ExampleSynchronousThing()
        self.thimble = Thimble(self.reactor, self.pool, self.wrapped, ["blocking_method"])

class AttributeAccessTests(_TestSetupMixin, SynchronousTestCase):
    def test_blocking_method(self):
        """A blocking method is wrapped so that it is executed in the thread
        pool.

        """
        d = self.thimble.blocking_method(1, second=2)
        self.assertEqual(self.successResultOf(d), 3)


    def test_non_blocking_property(self):
        """A non-blocking property is accessed directly.

        """
        self.assertEqual(self.thimble.non_blocking_property, 123)


    def test_accessing_wrapped_attribute(self):
        """Accessing the attribute of the :class:`Thimble` which also happens
        to be the name of attribute of the wrapped object (such as
        ``wrapped``) returns the attribute of the :class:`Thimble`.

        """
        self.assertIdentical(self.thimble._wrapped, self.wrapped)
        self.assertIdentical(self.thimble._wrapped._wrapped, None)



class ThreadPoolStartAndCleanupTests(_TestSetupMixin, SynchronousTestCase):
    def test_already_started(self):
        """When deferring something to the thread pool, and that thread pool
        is already started, it is not started again, and its shutdown
        is not scheduled.

        """
        self.pool.start()
        self.assertTrue(self.pool.started)
        self.assertEqual(self.reactor.eventTriggers, [])

        self.thimble.blocking_method(1, 2)

        self.assertTrue(self.pool.started)
        self.assertEqual(self.reactor.eventTriggers, [])

    def test_not_started_yet(self):
        """When deferring something to the thread pool, and that thread pool
        is not started yet, it is started, and its shutdown is scheduled.

        """
        self.assertFalse(self.pool.started)
        self.assertEqual(self.reactor.eventTriggers, [])

        self.thimble.blocking_method(1, second=2)

        self.assertTrue(self.pool.started)

        self.assertEqual(len(self.reactor.eventTriggers), 1)
        phase, eventType, _f, _args, _kwargs = self.reactor.eventTriggers[0]
        self.assertEqual(phase, "before")
        self.assertEqual(eventType, "shutdown")

        self.reactor.stop()
        self.assertFalse(self.pool.started)


class PublicAPITests(SynchronousTestCase):
    """
    Tests for accessing thimble's public API.
    """
    def test_from_wrapper_module(self):
        """
        :class:`Thimble` can also be imported from the ``wrapper`` module.
        """
        from thimble.wrapper import Thimble as Thimble2
        self.assertIdentical(Thimble, Thimble2)


    def test_exported_in_dunder_all(self):
        """
        :class:`Thimble` is in ``thimble.__all__``.
        """
        from thimble import __all__
        self.assertIn("Thimble", __all__)
