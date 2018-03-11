# Simple and powerful tagging for Python objects.
#
# Author: Peter Odding <peter@peterodding.com>
# Last Change: March 11, 2018
# URL: https://github.com/xolox/python-gentag

"""Custom exceptions raised by :mod:`gentag`."""

# Public identifiers that require documentation.
__all__ = (
    'GenTagError',
    'EmptyTagError',
    'TagExpressionError',
)


class GenTagError(Exception):

    """Base class for custom exceptions."""


class EmptyTagError(GenTagError):

    """Raised by :func:`~gentag.ObjectFactory.__getitem__()` when an empty tag is encountered during evaluation."""


class TagExpressionError(GenTagError):

    """Raised by :func:`~gentag.Scope.evaluate_raw()` when a string expression contains syntax errors."""
