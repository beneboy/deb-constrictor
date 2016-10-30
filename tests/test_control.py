import unittest
import mock
from constrictor.control import BinaryControl

"""Package (mandatory)
Source
Version (mandatory)
Section (recommended)
Priority (recommended)
Architecture (mandatory)
Essential
Depends et al
Installed-Size
Maintainer (mandatory)
Description (mandatory)
Homepage
Built-Using"""


class TestBinaryControl(unittest.TestCase):
    def setUp(self):
        self.control = BinaryControl("test-package", "1.0.5", "amd64", "Johnny Coder",
                                     "This is a test package for fun.")

    def test_generate_control_text_with_required_only(self):
        expected_text = "Package: test-package\nVersion: 1.0.5\nArchitecture: amd64\nMaintainer: Johnny Coder\n" \
                        "Description: This is a test package for fun.\n"

        self.assertEqual(self.control.get_control_text(), expected_text)

    def test_installed_size_bytes_is_not_added_by_default(self):
        self.assertNotIn("Installed-Size:", self.control.get_control_text())
        self.control.installed_size_bytes = 2048
        self.assertIn("Installed-Size: 2", self.control.get_control_text())

    def test_overridden_installed_size_overrides_attribute(self):
        """If Installed-Size is set on the extra control dict then it should override installed_size_bytes attributes"""
        self.control.installed_size_bytes = 2048
        self.control.set_control_field('Installed-Size', 4096)
        self.assertIn("Installed-Size: 4096", self.control.get_control_text())

    def test_value_error_on_invalid_control_set(self):
        with self.assertRaises(KeyError):
            self.control.set_control_field('FooBar', 45)

    def test_converts_package_list_to_comma_separated(self):
        package_list = ('linux-core', 'python-core', 'ruby')

        for pkg_list_field in ("Pre-Depends", "Enhances", "Suggests", "Recommends", "Depends", "Breaks", "Conflicts",
                               "Provides", "Replaces"):
            self.control.set_control_field(pkg_list_field, package_list)

            expected = "{}: linux-core, python-core, ruby".format(pkg_list_field)

            self.assertIn(expected, self.control.get_control_text())

    def test_set_multiple_field_values(self):
        """Calling set_control_fields with a dict should call set_control_field with each key/value pair"""
        control_fields = {
            'Homepage': 'http://www.example.com',
            'Built-Using': 'DebConstrictor',
            'Description': "About the package."
        }

        self.control.set_control_field = mock.Mock()

        self.control.set_control_fields(control_fields)

        self.control.set_control_field.assert_any_call('Homepage', 'http://www.example.com')
        self.control.set_control_field.assert_any_call('Built-Using', 'DebConstrictor')
        self.control.set_control_field.assert_any_call('Description', 'About the package.')
