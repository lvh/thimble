=========
 thimble
=========

.. image:: https://travis-ci.org/lvh/thimble.svg
    :target: https://travis-ci.org/lvh/thimble
.. image:: https://coveralls.io/repos/lvh/thimble/badge.png
    :target: https://coveralls.io/r/lvh/thimble

.. image:: https://dl.dropboxusercontent.com/u/38476311/Logos/thimble.jpg

A thimble is a tool for playing with needle and thread safely. This
library, thimble, wraps objects that have a blocking API with a
non-blocking, Twisted-friendly Deferred API by means of thread pools.

Quick start
===========

The main object you're interested in is ``thimble.Thimble``. It takes a
thread pool, a blocking object, and a list of method names that you
would like to defer to the thread pool.

Here's our example blocking object:

>>> class Car(object):
...     wheels = 4
...     def drive_to(self, location):
...          # Assume the real implementation blocks.
...          return "driven to {0}".format(location)
>>> car = Car()

For demonstration purposes, we'll use a test doubles for the thread
pool and reactor; in real code, you'll want to use the real thing.

>>> from thimble.test.util import FakeThreadPool, FakeReactor
>>> pool = FakeThreadPool()
>>> reactor = FakeReactor()

The pool hasn't been started yet. (We'll see why that matters in a
minute.)

>>> pool.started
False

Create a ``Thimble``:

>>> from thimble import Thimble
>>> car_thimble = Thimble(reactor, pool, car, ["drive_to"])

When accessing a method named in the list, you get an object wrapping
it instead. Calling it returns a Deferred. Any arguments passed are
passed verbatim to the wrapped method.

>>> d = car_thimble.drive_to("work")
>>> d.result
'driven to work'

This Deferred has already fired synchronously, because we're using a
fake thread pool and reactor.

You can access other attributes of the wrapped object directly on the
``Thimble``:

>>> car.wheels
4

If the thread pool that you pass to a ``Thimble`` hasn't been started
yet when it first tries to use it, the ``Thimble`` will start it and
schedule its shutdown. If you pass a thread pool that *was* already
started, you are responsible for its shutdown. In this case, the
thread pool was not started yet, so ``Thimble`` started it for you:

>>> pool.started
True

Shut down the reactor, and the reactor will ask the thread pool to
stop right before shutting down itself.

>>> reactor.stop()
>>> pool.started
False

Using thimble in your code
--------------------------

Thread pools
~~~~~~~~~~~~

You can choose to use the reactor thread pool, or create your own
thread pool.

Using the reactor thread pool is potentially a bad idea. The reactor
thread pool is shared between a lot of software by default, and is
also used for DNS resolution. If your software blocks all the
available threads in the pool (either by accident or because of a
bug), that affects DNS resolution, which in turn can affect many other
systems.

Entry points
~~~~~~~~~~~~

While subclassing ``Thimble`` may accidentally work, it is not
recommended. I reserve the right to change the implementation in a way
that might break that: for example, by introducing a metaclass.

It's probably better to write a small utility function that either
constructs a new thread pool from a shared thread pool, or always
returns the same thimble.

Changelog
=========

Thimble uses SemVer_.

.. _SemVer: http://semver.org/

v0.1.1 (WIP)
------------

- Added this changelog
- Spelling fixes

v0.1.0
------

Initial public release.
