from twisted.trial.unittest import SynchronousTestCase
from thimble import Thimble
from thimble.test.util import FakeReactor, FakeThreadPool
from twisted.internet.error import ReactorNotRunning


class ExampleSynchronousThing(object):

    """
    An example thing with some blocking APIs which will be wrapped and
    some non-blocking (but still synchronous, i.e. not returning
    Deferreds) APIs that won't be.
    """

    @property
    def _wrapped(self):
        """
        This is here to verify that the ``_wrapped`` attribute of the
        :class:`Thimble` is used before the ``_wrapped`` attribute of
        the wrapped object.
        """
        return None

    @property
    def non_blocking_property(self):
        """A property that doesn't block.

        It is *synchronous*, it just doesn't
        block long enough to warrant wrapping it in a thread pool.

        """
        return 123

    def blocking_method(self, first, second):
        """A blocking method that adds two numbers."""
        return first + second

    def hooked_method(self, number):
        """A non-blocking method that just returns the given number."""
        return number

    def hooked_blocking_method(self, number):
        """A blocking method that just returns the given number."""
        return number


class _TestSetupMixin(object):

    def setUp(self):
        self.reactor = FakeReactor()
        self.pool = FakeThreadPool()
        self.wrapped = ExampleSynchronousThing()
        self.thimble = Thimble(self.reactor,
                               self.pool,
                               self.wrapped,
                               ['blocking_method',
                                'hooked_blocking_method'],
                               dict.fromkeys(["hooked_method",
                                              "hooked_blocking_method"],
                                             self.hook))
        self.expected_attr = None

    def hook(self, thimble, attr, val):
        self.assertIdentical(thimble, self.thimble)
        self.assertIdentical(attr, self.expected_attr)
        return lambda x: val(x + 1)


class LegacySignatureTests(SynchronousTestCase):
    def test_without_attr_hooks(self):
        """
        Instantiating a thimble without the attr_hooks attribute works.

        If no attr hooks are specified, the thimble gets a new, empty
        dict as their attr hooks.
        """
        thimble = Thimble(None, None, None, [])
        self.assertEqual(thimble._attr_hooks, {})
        thimble2 = Thimble(None, None, None, [])
        self.assertEqual(thimble2._attr_hooks, {})
        self.assertNotIdentical(thimble._attr_hooks, thimble2._attr_hooks)


class AttributeAccessTests(_TestSetupMixin, SynchronousTestCase):

    def test_blocking_method(self):
        """
        A blocking method is wrapped so that it is executed in the thread
        pool.
        """
        d = self.thimble.blocking_method(1, second=2)
        self.assertEqual(self.successResultOf(d), 3)

    def test_non_blocking_property(self):
        """A non-blocking property is accessed directly."""
        self.assertEqual(self.thimble.non_blocking_property, 123)

    def test_accessing_wrapped_attribute(self):
        """
        Accessing the attribute of the :class:`Thimble` which also happens
        to be the name of attribute of the wrapped object (such as
        ``wrapped``) returns the attribute of the :class:`Thimble`.
        """
        self.assertIdentical(self.thimble._wrapped, self.wrapped)
        self.assertIdentical(self.thimble._wrapped._wrapped, None)

    def test_hooked_method(self):
        """
        When accessing a (non-blocking) method/attribute with a registered
        hook, the hook is invoked.
        """
        attr = "hooked_method"

        before_hook = getattr(self.thimble._wrapped, attr)
        self.assertEqual(before_hook(1), 1)

        self.expected_attr = attr
        self.assertEqual(getattr(self.thimble, attr)(1), 2)

    def test_hooked_blocking_method(self):
        """
        When accessing a blocking method with a registered hook, the hook is
        invoked.
        """
        attr = "hooked_blocking_method"

        before_hook = getattr(self.thimble._wrapped, attr)
        self.assertEqual(before_hook(1), 1)

        self.expected_attr = attr

        d = getattr(self.thimble, attr)(1)
        self.assertEqual(self.successResultOf(d), 2)


class ThreadPoolStartAndCleanupTests(_TestSetupMixin, SynchronousTestCase):

    def test_already_started(self):
        """When deferring something to the thread pool, and that thread pool is
        already started, it is not started again, and its shutdown is not
        scheduled."""
        self.pool.start()
        self.assertTrue(self.pool.started)
        self.assertEqual(self.reactor.eventTriggers, [])

        self.thimble.blocking_method(1, 2)

        self.assertTrue(self.pool.started)
        self.assertEqual(self.reactor.eventTriggers, [])

    def test_not_started_yet(self):
        """When deferring something to the thread pool, and that thread pool is
        not started yet, it is started, and its shutdown is scheduled."""
        self.assertFalse(self.pool.started)
        self.assertEqual(self.reactor.eventTriggers, [])

        self.thimble.blocking_method(1, second=2)

        self.assertTrue(self.pool.started)

        self.assertEqual(len(self.reactor.eventTriggers), 1)
        phase, eventType, _f, _args, _kwargs = self.reactor.eventTriggers[0]
        self.assertEqual(phase, 'during')
        self.assertEqual(eventType, 'shutdown')

        self.reactor.stop()
        self.assertFalse(self.pool.started)

    def test_stopping(self):
        """
        When deferring something to the thread pool, if that thread pool has
        been stopped already, the ``Deferred`` will fail with a
        ``ReactorNotRunning`` exception.
        """
        result1 = self.thimble.blocking_method(1, second=2)
        self.successResultOf(result1)
        self.reactor.stop()
        self.assertFalse(self.pool.started)
        self.assertTrue(self.pool.joined)

        result2 = self.thimble.blocking_method(3, second=4)
        self.failureResultOf(result2, ReactorNotRunning)


class PublicAPITests(SynchronousTestCase):

    """Tests for accessing thimble's public API."""

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
        self.assertIn('Thimble', __all__)
