"""Tests for the test utilities."""
from thimble.test.util import FakeReactor
from twisted.trial.unittest import SynchronousTestCase


class FakeReactorTests(SynchronousTestCase):
    def setUp(self):
        self.reactor = FakeReactor()

    def _trigger(self, *args, **kwargs):
        """An example trigger."""
        self.trigger_call_args = args, kwargs

    def test_shutdown_events(self):
        """Shutting down the reactor calls the registered events.

        Specifically, shutdown events are called and non-shutdown
        events are not called.

        """
        self.trigger_call_args = None
        self.reactor.addSystemEventTrigger("before", "shutdown",
                                           self._trigger, 1, x=2)
        self.reactor.addSystemEventTrigger("after", "startup",
                                           self.fail)

        self.reactor.stop()

        args, kwargs = self.trigger_call_args
        self.assertEqual(args, (1,))
        self.assertEqual(kwargs, {"x": 2})
