# Simple and powerful tagging for Python objects.
#
# Author: Peter Odding <peter@peterodding.com>
# Last Change: March 4, 2018
# URL: https://github.com/xolox/python-gentag

"""
The test suite for :mod:`gentag`.

The online documentation includes the full source code of the test suite
because it provides examples of how to use the :mod:`gentag` module.
"""

# External dependencies.
from humanfriendly.testing import TestCase

# The module we're testing.
from gentag import Scope, Tag, generate_id
from gentag.exceptions import EmptyTagError, TagExpressionError


class GenTagTestCase(TestCase):

    """A :mod:`unittest` compatible container for the :mod:`gentag` test suite."""

    def setUp(self):
        """Define a new :class:`.Scope` for every test method."""
        self.scope = Scope()

    def test_add_object(self):
        """Test the :func:`~gentag.Scope.add_object()` method."""
        self.scope.add_object(1, 'a', 'b')
        self.scope.add_object(2, 'b', 'c')
        self.scope.add_object(3, 'c', 'd')
        self.scope.add_object(4, 'd', 'e')
        self.assertEquals(
            self.scope.evaluate('c'),
            [2, 3],
        )

    def test_default_tag(self):
        """Test that the default tag matches all tagged objects."""
        self.scope.define('a', [1, 2])
        self.scope.define('b', [3, 4])
        self.scope.define('c', [5, 6])
        self.assertEquals(self.scope.evaluate('all'), [1, 2, 3, 4, 5, 6])
        self.assertEquals(self.scope.evaluate('all - b'), [1, 2, 5, 6])

    def test_define_expression(self):
        """Test the definition of a composite tag."""
        self.scope.define('a', [1, 2])
        self.scope.define('b', [3, 4])
        self.scope.define('c', 'a | b')
        self.assertEquals(self.scope.evaluate('c'), [1, 2, 3, 4])

    def test_define_unsupported(self):
        """Test the definition of a tag with an unsupported value type."""
        self.assertRaises(ValueError, self.scope.define, 'a', None)

    def test_difference_expression(self):
        """Get the difference of two tags (using a Python expression)."""
        a = self.scope.define('a', [1, 2, 3, 4])
        b = self.scope.define('b', [3, 4, 5, 6])
        self.assertEquals((a - b).objects, set([1, 2]))

    def test_difference_string(self):
        """Get the difference of two tags (using a string expression)."""
        self.scope.define('a', [1, 2, 3, 4])
        self.scope.define('b', [3, 4, 5, 6])
        self.assertEquals(self.scope.evaluate('a - b'), [1, 2])

    def test_empty_tag(self):
        """Test which exception is raised when a tag has no associated objects."""
        self.assertRaises(EmptyTagError, self.scope.evaluate, 'a')

    def test_generate_id(self):
        """Test the :func:`~gentag.generate_id()` function."""
        self.assertEquals(generate_id('Some random name!', normalized=True), 'somerandomname')
        self.assertEquals(generate_id('Some random name!', normalized=False), 'some_random_name')
        self.assertEquals(generate_id('42', normalized=False), '_42')
        self.assertRaises(ValueError, generate_id, '', normalized=True)

    def test_intersection_expression(self):
        """Get the intersection of two tags (using a Python expression)."""
        a = self.scope.define('a', [1, 2, 3, 4])
        b = self.scope.define('b', [3, 4, 5, 6])
        self.assertEquals((a & b).objects, set([3, 4]))

    def test_intersection_string(self):
        """Get the intersection of two tags (using a string expression)."""
        self.scope.define('a', [1, 2, 3, 4])
        self.scope.define('b', [3, 4, 5, 6])
        self.assertEquals(self.scope.evaluate('a & b'), [3, 4])

    def test_iterable(self):
        """Test that tags can be iterated to get th matching objects."""
        a = self.scope.define('a', [1, 2, 3, 4])
        self.assertEquals(list(a), [1, 2, 3, 4])

    def test_not_implemented(self):
        """Check that composition with other types is forbidden."""
        a = self.scope.define('a', [1, 2])
        self.assertRaises(TypeError, lambda: a | set())

    def test_parentheses(self):
        """Check that parentheses are used appropriately."""
        # Define some tags to work with.
        a = self.scope.define('a', [1, 2])
        b = self.scope.define('b', [2, 3])
        c = self.scope.define('c', [3, 4])
        d = self.scope.define('d', [4, 5])
        # Define a composite tag as a Python expression.
        e = (a | b) | (c & d)
        # Check the generated string expression to ensure that precedence is
        # being preserved by the use of parentheses in the right places.
        self.assertEquals(e.expression, '(a | b) | (c & d)')
        # Sanity check the result of the evaluation.
        self.assertEquals(e.objects, set([1, 2, 3, 4]))

    def test_parse_expression(self):
        """Test the parsing of expressions."""
        value = self.scope.parse('(a | b)')
        self.assertIsInstance(value, Tag)
        self.assertEquals(value.expression, 'a | b')

    def test_parse_invalid(self):
        """Test which exception is raised on invalid types by :func:`~gentag.Scope.parse()`."""
        self.assertRaises(ValueError, self.scope.parse, None)

    def test_sorting(self):
        """Test natural order sorting of string objects."""
        self.scope.define('a', ['server-1', 'server-5'])
        self.scope.define('b', ['server-11', 'server-15'])
        self.assertEquals(
            self.scope.evaluate('a | b'),
            ['server-1', 'server-5', 'server-11', 'server-15'],
        )

    def test_symmetric_difference_expression(self):
        """Get the symmetric difference of two tags (using a Python expression)."""
        a = self.scope.define('a', [1, 2, 3, 4])
        b = self.scope.define('b', [3, 4, 5, 6])
        self.assertEquals((a ^ b).objects, set([1, 2, 5, 6]))

    def test_symmetric_difference_string(self):
        """Get the symmetric difference of two tags (using a string expression)."""
        self.scope.define('a', [1, 2, 3, 4])
        self.scope.define('b', [3, 4, 5, 6])
        self.assertEquals(self.scope.evaluate('a ^ b'), [1, 2, 5, 6])

    def test_syntax_error(self):
        """Test which exception is raised on syntax errors."""
        self.assertRaises(TagExpressionError, self.scope.evaluate, 'all - ')

    def test_union_expression(self):
        """Get the union of two tags (using a Python expression)."""
        a = self.scope.define('a', [1, 2])
        b = self.scope.define('b', [3, 4])
        self.assertEquals((a | b).objects, set([1, 2, 3, 4]))

    def test_union_string(self):
        """Get the union of two tags (using a string expression)."""
        self.scope.define('a', [1, 2])
        self.scope.define('b', [3, 4])
        self.assertEquals(self.scope.evaluate('a | b'), [1, 2, 3, 4])
