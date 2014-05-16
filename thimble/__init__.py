"""A Twisted thread-pool based wrapper for blocking APIs."""
from ._version import __version__
version = __version__

from .wrapper import Thimble
__all__ = ['Thimble']
