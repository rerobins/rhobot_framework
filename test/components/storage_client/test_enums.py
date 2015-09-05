"""
Test enumerations for the flags and their utility classes.
"""
import unittest
from rhobot.components.storage.enums import Flag
import enum


class EnumerationTestCase(unittest.TestCase):

    def test_flag_mixin(self):

        field_type = 'boolean'
        var = 'some_var_name'
        default_value = 'default_value'

        class TestEnumeration(Flag, enum.Enum):
            TEST_ENUM = (var, field_type, default_value)

        self.assertEqual(TestEnumeration.TEST_ENUM.var, var)
        self.assertEqual(TestEnumeration.TEST_ENUM.field_type, field_type)
        self.assertEqual(TestEnumeration.TEST_ENUM.default, default_value)

