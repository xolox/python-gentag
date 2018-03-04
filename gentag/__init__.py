# Simple and powerful tagging for Python objects.
#
# Author: Peter Odding <peter@peterodding.com>
# Last Change: March 4, 2018
# URL: https://github.com/xolox/python-gentag

"""Simple and powerful tagging for Python objects."""

# Standard library modules.
import collections
import re

# External dependencies.
from humanfriendly import format, pluralize
from natsort import natsort
from property_manager import (
    PropertyManager,
    clear_property,
    lazy_property,
    mutable_property,
    required_property,
    set_property,
)
from six import string_types
from verboselogs import VerboseLogger

# Modules included in our package.
from gentag.exceptions import EmptyTagError, TagExpressionError

DEFAULT_TAG_NAME = 'all'
"""The identifier of the default tag that matches all tagged objects (a string)."""

# Semi-standard module versioning.
__version__ = '1.0'

# Initialize a logger for this module.
logger = VerboseLogger(__name__)


class Scope(PropertyManager):

    """
    To use :mod:`gentag` everything starts with a :class:`Scope` object.

    A :class:`Scope` object groups together related :class:`Tag` objects
    and provides methods to define new tags and evaluate tag expressions.
    """

    @property
    def objects(self):
        """A mapping of tag names to :class:`set` objects (an :class:`ObjectFactory` instance)."""
        return ObjectFactory(tags=self.tags)

    @lazy_property
    def tags(self):
        """A mapping of tag names to :class:`Tag` objects (an :class:`TagFactory` instance)."""
        return TagFactory(scope=self)

    def add_object(self, value, *tags):
        """
        Add an object to the scope.

        :param value: The object to add (any hashable value).
        :param tags: The names of tags to associate the object with.
        """
        logger.debug("Tagging object %r with %s: %s",
                     value, pluralize(len(tags), "tag"),
                     ", ".join(map(str, tags)))
        for name in tags:
            self.tags[name].objects.add(value)

    def define(self, name, value):
        """
        Define the value of a tag.

        :param name: The name of the tag (a string).
        :param value: A string containing an expression or an iterable
                      of values associated to the given tag.
        :returns: The :class:`Tag` object.
        :raises: :exc:`~exceptions.ValueError` for unsupported `value` types.
        """
        if isinstance(value, string_types):
            logger.debug("Setting expression of tag '%s' to: %s", name, value)
            tag = self.tags[name]
            tag.expression = value
            return tag
        elif isinstance(value, collections.Iterable):
            logger.debug("Setting objects of tag '%s' to: %s", name, value)
            tag = self.tags[name]
            tag.objects = value
            return tag
        else:
            msg = "Unsupported value for tag '%s'! (%r)"
            raise ValueError(format(msg, name, value))

    def evaluate(self, expression):
        """
        Get the objects matching the given expression.

        :param expression: The tag expression to evaluate (a string).
        :returns: A sorted :class:`list` with matching objects.
        :raises: :exc:`.TagExpressionError` when the given expression
                 cannot be evaluated due to a syntax error.

        This method is a wrapper for :func:`evaluate_raw()` that calls
        :func:`sorted()` on the matching objects before returning them.
        """
        return self.sorted(self.evaluate_raw(expression))

    def evaluate_raw(self, expression):
        """
        Get the objects matching the given expression.

        :param expression: The tag expression to evaluate (a string).
        :returns: A :class:`set` with matching objects.
        :raises: :exc:`.TagExpressionError` when the given expression
                 cannot be evaluated due to a syntax error.

        This method uses :func:`eval()` to evaluate the expression given by the
        caller, however it overrides ``__builtins__`` to avoid leaking any
        built-ins into the :func:`eval()` call.
        """
        try:
            logger.debug("Evaluating expression '%s' ..", expression)
            objects = eval(expression, dict(__builtins__={}), self.objects)
            logger.debug("The expression matched %s.", pluralize(len(objects), "object"))
            return objects
        except SyntaxError as e:
            msg = "Failed to evaluate tag expression due to syntax error! (%s)"
            raise TagExpressionError(format(msg, e))

    def get_all_objects(self):
        """
        Get all objects defined in the scope.

        :returns: A :class:`set` of user defined objects.

        This method iterates over the defined tags and collects all tagged
        objects. Because the evaluation of tags with an :attr:`~Tag.expression`
        won't change the result of :func:`get_all_objects()` such tags are
        skipped for performance reasons.
        """
        objects = set()
        logger.debug("Collecting all tagged objects ..")
        for tag in self.tags:
            if tag.identifier != DEFAULT_TAG_NAME and not tag.expression:
                objects.update(tag.objects)
        logger.debug("Collected %s.", pluralize(len(objects), "object"))
        return objects

    def parse(self, value):
        """
        Parse a string expression into a :class:`Tag` object.

        :param value: The tag expression to parse (a string).
        :returns: A :class:`Tag` object.
        :raises: :exc:`~exceptions.ValueError` for unsupported `value` types.

        During normal use you won't need the :func:`parse()` method, in fact
        it's not currently being used anywhere in :mod:`gentag`. This method
        was originally created with the idea of having :func:`define()` parse
        string expressions up front to validate their syntax, however this
        approach has since been abandoned. The :func:`parse()` method now
        remains because it may be useful to callers for unforeseen use cases.
        """
        if isinstance(value, string_types):
            # We override __builtins__ to avoid leaking any built-ins into eval().
            return eval(value, dict(__builtins__={}), self.tags)
        else:
            msg = "Unsupported value type! (%r)"
            raise ValueError(format(msg, value))

    def sorted(self, objects):
        """
        Sort the given objects in a human friendly way.

        :param objects: The objects to sort (an iterable).
        :returns: The sorted objects (a list).

        If all of the objects are strings they are sorted using natural
        order sorting, otherwise the :func:`sorted()` function is used.
        """
        if all(isinstance(o, string_types) for o in objects):
            return natsort(objects)
        else:
            return sorted(objects)


class Tag(PropertyManager):

    """
    A :class:`Tag` represents a set of :attr:`objects` with a common :attr:`name`.

    There are three kinds of tags:

    **Simple tags:**
     When you set :attr:`objects` the tag becomes a 'simple tag' that
     associates the name of the tag to the given objects.

    **Composite tags:**
     When you set :attr:`expression` the tag becomes a 'composite tag' that
     associates the name of the tag to an expression that selects a subset of
     tagged objects.

    **The special default tag:**
     When :attr:`identifier` is set to :data:`DEFAULT_TAG_NAME` the value of
     :attr:`objects` is a :class:`set` that contains all tagged objects.
    """

    @mutable_property
    def expression(self):
        """A Python expression to select matching objects (a string or :data:`None`)."""

    @expression.setter
    def expression(self, value):
        """Set `expression` and clear `objects`."""
        set_property(self, 'expression', value)
        clear_property(self, 'id_or_expr')
        clear_property(self, 'objects')

    @lazy_property
    def identifier(self):
        """An identifier based on :attr:`name` (a string or :data:`None`)."""
        if self.name:
            return generate_id(self.name, normalized=False)

    @lazy_property
    def id_or_expr(self):
        """
        The :attr:`identifier` (if set) or :attr:`expression` (a string).

        The value of :attr:`id_or_expr` is used by :func:`compose()` to
        generate :attr:`expression` values for composite :class:`Tag`
        objects.
        """
        if self.identifier:
            return self.identifier
        else:
            expr = self.expression
            if not (expr.isalnum() or (expr.startswith('(') and expr.endswith(')'))):
                # Add parentheses to ensure the right evaluation order.
                expr = '(%s)' % expr
            return expr

    @mutable_property
    def name(self):
        """
        A user defined name for the tag (a string or :data:`None`).

        Tags created using :func:`~Scope.define()` always have :attr:`name` set
        but tags composed using Python expression syntax are created without a
        :attr:`name`.
        """

    @name.setter
    def name(self, value):
        """Set `name` and `identifier`."""
        set_property(self, 'name', value)
        clear_property(self, 'id_or_expr')
        clear_property(self, 'identifier')

    @mutable_property
    def objects(self):
        """
        The values associated to the tag (a :class:`set`).

        If :attr:`objects` isn't set it defaults to a computed value:

        - If :attr:`identifier` is :data:`DEFAULT_TAG_NAME` then
          :func:`~Scope.get_all_objects()` is used
          to get the associated values.

        - If :attr:`expression` is set it will be evaluated and the matching
          objects will be returned.

        - Otherwise a new, empty :class:`set` is created, bound to the
          :class:`Tag` and returned.
        """
        if self.identifier == DEFAULT_TAG_NAME:
            return self.scope.get_all_objects()
        elif self.expression:
            return self.scope.evaluate_raw(self.expression)
        else:
            value = set()
            set_property(self, 'objects', value)
            return value

    @objects.setter
    def objects(self, value):
        """Set `objects` and clear `expression`."""
        set_property(self, 'objects', set(value))
        clear_property(self, 'id_or_expr')
        clear_property(self, 'expression')

    @required_property(repr=False)
    def scope(self):
        """The :class:`Scope` in which the tag has been defined."""

    def compose(self, operator, other):
        """
        Create a composite tag.

        :param operator: The operator used to compose the tags (a string).
        :param other: The other :class:`Tag` object.
        :returns: A new :class:`Tag` object or :data:`NotImplemented`
                  (if `other` isn't a :class:`Tag` object).

        The :func:`compose()` method is a helper for :func:`__and__()`,
        :func:`__or__()`, :func:`__sub__()` and :func:`__xor__()` that
        generates an :attr:`expression` based on the :attr:`id_or_expr`
        values of the two :class:`Tag` objects.
        """
        if isinstance(other, Tag):
            expression = '%s %s %s' % (self.id_or_expr, operator, other.id_or_expr)
            return Tag(expression=expression, scope=self.scope)
        else:
            return NotImplemented

    def __and__(self, other):
        """Use :func:`compose()` to create a :class:`Tag` that gives the intersection of two :class:`Tag` objects."""
        return self.compose('&', other)

    def __iter__(self):
        """Iterate over the matching objects."""
        return iter(self.scope.sorted(self.objects))

    def __or__(self, other):
        """Use :func:`compose()` to create a :class:`Tag` that gives the union of two tags."""
        return self.compose('|', other)

    def __sub__(self, other):
        """Use :func:`compose()` to create a :class:`Tag` that gives the difference of two tags."""
        return self.compose('-', other)

    def __xor__(self, other):
        """Use :func:`compose()` to create a :class:`Tag` that gives the symmetric difference of two tags."""
        return self.compose('^', other)


class TagFactory(PropertyManager):

    """
    A mapping of tag names to :class:`Tag` objects.

    The names of tags are normalized using :func:`generate_id()`.
    """

    @lazy_property
    def map(self):
        """A dictionary with tags created by this :class:`TagFactory`."""
        return {}

    @required_property(repr=False)
    def scope(self):
        """The :class:`Scope` that's using this :class:`TagFactory`."""

    def __getitem__(self, name):
        """
        Get or create a tag.

        :param name: The name of the tag (a string).
        :returns: A :class:`Tag` object.
        """
        key = generate_id(name, normalized=True)
        value = self.map.get(key)
        if value is None:
            logger.debug("Creating tag on first use: %s", name)
            value = Tag(name=name, scope=self.scope)
            self.map[key] = value
        return value

    def __iter__(self):
        """Iterate over the defined :class:`Tag` objects."""
        return iter(self.map.values())


class ObjectFactory(PropertyManager):

    """
    A mapping of tag names to :class:`set` objects.

    This class is used by :func:`~Scope.evaluate()` during expression
    parsing to resolve tag names to the associated :attr:`~Tag.objects`.
    """

    @required_property
    def tags(self):
        """The :class:`TagFactory` from which objects are retrieved."""

    def __getitem__(self, name):
        """
        Get the objects associated to the given tag.

        :param name: The name of the tag (a string).
        :returns: A :class:`set` of objects associated to the tag.
        :raises: :exc:`.EmptyTagError` when no associated objects are available.
        """
        objects = self.tags[name].objects
        if not objects:
            msg = "The tag '%s' doesn't match anything!"
            raise EmptyTagError(format(msg, name))
        return objects


def generate_id(value, normalized):
    """
    Generate a Python identifier from a user provided string.

    :param value: The user provided string.
    :param normalized: :data:`True` to normalize the identifier to its
                       canonical form without underscores, :data:`False`
                       to preserve some readability.
    :returns: The generated identifier (a string).
    :raises: :exc:`~exceptions.ValueError` when nothing remains of `value`
             after normalization.

    If you just want a Python identifier from a user
    defined string you can use `normalized=False`:

    >>> generate_id('Any user-defined string', normalized=False)
    'any_user_defined_string'

    However if you want to use the identifier for comparison or as
    a key in a dictionary then its better to use `normalized=True`:

    >>> generate_id('Any user-defined string', normalized=True)
    'anyuserdefinedstring'

    The following example shows that values that would otherwise start with a
    digit are prefixed with an underscore, because Python identifiers cannot
    start with a digit:

    >>> generate_id('42', normalized=True)
    '_42'
    """
    value = str(value).lower()
    # Replace characters not allowed in identifiers with an underscore.
    value = re.sub('[^a-z0-9]+', '' if normalized else '_', value)
    # Strip leading and/or trailing underscores.
    value = value.strip('_')
    # Make sure something remains from the user provided string.
    if not value:
        msg = "Nothing remains of the given string after normalization! (%r)"
        raise ValueError(msg % value)
    # Add a leading underscore when the first character is a digit.
    if value[0].isdigit():
        value = '_' + value
    return value
