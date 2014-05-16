"""Stubs and other utilities for thimble's test suite."""


class FakeThreadPool(object):

    """Fake thread pool for testing purposes.

    It pretends to let you call objects with some arguments in a
    thread with a callback, but just does all of that synchronously in
    the calling thread.

    """

    def __init__(self):
        """Initialize the fake thread pool."""
        self.started = False
        self.success = True

    def start(self):
        """Set the ``started`` attribute to ``True``."""
        self.started = True

    def stop(self):
        """Set the ``started`` attribute to ``True``."""
        self.started = False

    def callInThreadWithCallback(self, onResult, f, *args, **kwargs):
        """Evaluate ``f(*args, **kwargs)`` and calls ``onResult``.

        This happens synchronously and in the current thread.

        """
        onResult(self.success, f(*args, **kwargs))


class FakeReactor(object):

    """A fake reactor for testing purposes.

    It pretends to be able to be called from a thread, and knows how to
    add event triggers.

    """

    def __init__(self):
        """Initialize the fake reactor."""
        self.eventTriggers = []

    def callFromThread(self, f, *a, **kw):
        """Just call the function synchronously in this thread."""
        f(*a, **kw)

    def addSystemEventTrigger(self, phase, eventType, f, *args, **kw):
        """Store the event trigger."""
        trigger = phase, eventType, f, args, kw
        self.eventTriggers.append(trigger)

    def stop(self):
        """Run the shutdown event triggers."""
        for phase, eventType, f, args, kwargs in self.eventTriggers:
            if eventType != 'shutdown':
                continue

            f(*args, **kwargs)
