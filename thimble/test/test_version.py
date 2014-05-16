from thimble import __version__, version, _version
from twisted.trial.unittest import SynchronousTestCase


class VersionTests(SynchronousTestCase):

    """Tests for programmatically acquiring the version of ``thimble``."""

    def test_both_names(self):
        """The version is programmatically avaialble on the ``txkazoo`` module
        as ``__version__`` and ``version``.

        They are the same object.

        """
        self.assertIdentical(__version__, version)

    def test_module(self):
        """The version is programmatically available on the ``_version``
        internal module."""
        self.assertIdentical(__version__, _version.__version__)
