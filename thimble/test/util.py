class FakeThreadPool(object):
    """Fake thread pool for testing purposes.

    A fake thread pool that pretends to let you call things in a
    thread with a callback. It calls the callback synchronously.

    """
    def __init__(self):
        self.started = False
        self.success = True

    def start(self):
        """Sets the ``started`` attribute to ``True``.

        """
        self.started = True

    def stop(self):
        """Sets the ``started`` attribute to True.

        """
        self.started = False

    def callInThreadWithCallback(self, onResult, f, *args, **kwargs):
        """Remembers ``f, args, kwargs``, then synchronously evaluates
        ``f(*args, **kwargs)`` in the current thread and calls the
        callback with the result.

        """
        onResult(self.success, f(*args, **kwargs))



class FakeReactor(object):
    """A fake reactor for testing purposes. It pretends to be able to be
    called from a thread, and knows how to add event triggers.

    """
    def __init__(self):
        self.eventTriggers = []


    def callFromThread(self, f, *a, **kw):
        """
        Just call the function in this thread.
        """
        f(*a, **kw)


    def addSystemEventTrigger(self, phase, eventType, callable, *args, **kw):
        """
        Stores the event trigger.
        """
        trigger = phase, eventType, callable, args, kw
        self.eventTriggers.append(trigger)
