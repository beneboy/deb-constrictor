import unittest
from constrictor.configuration import ConstrictorConfiguration


class TestConfiguration(unittest.TestCase):
    def test_update_deb_constrictor_configuration_override(self):
        cc = ConstrictorConfiguration({})

        cc.update_configuration({
             "deb_constrictor": {
                 "ignore_paths": ["a", "b", "c"]
             }
        })

        cc.update_configuration({
             "deb_constrictor": {
                 "ignore_paths": ["c", "d", "e"]
             }
        })

        combined_paths = cc['deb_constrictor']['ignore_paths']

        self.assertEqual(5, len(combined_paths), "Length should be the number of unique entries.")
        self.assertIn("a", combined_paths)
        self.assertIn("b", combined_paths)
        self.assertIn("c", combined_paths)
        self.assertIn("d", combined_paths)
        self.assertIn("e", combined_paths)

    def test_update_extra_control_fields(self):
        cc = ConstrictorConfiguration({})

        cc.update_configuration({
            "extra_control_fields": {
                "Section": "misc",
                "Provides": ["a"],
                "Depends": ["b"],
                "Priority": "optional"
            }
        })

        cc.update_configuration({
            "extra_control_fields": {
                "Section": "servers",
                "Provides": ["c"],
                "Depends": ["d"]
            }
        })

        extra_control_fields = cc['extra_control_fields']

        self.assertEqual({
            "Section": "servers",
            "Provides": ["a", "c"],
            "Depends": ["b", "d"],
            "Priority": "optional"
        }, extra_control_fields)

    def test_update_directories(self):
        cc = ConstrictorConfiguration({})

        cc.update_configuration({
            "directories": [
                {
                    "source": "a",
                    "destination": "b",
                    "uname": "a"
                },
                {
                    "source": "a/",
                    "destination": "c"
                }
            ]
        })

        cc.update_configuration({
            "directories": [
                {
                    "source": "a/",
                    "destination": "b/",
                    "uname": "b"
                },
                {
                    "source": "a/",
                    "destination": "d"
                }
            ]
        })

        directories = cc['directories']

        self.assertEqual([
            {
                "source": "a/",
                "destination": "c"
            },
            {
                "source": "a/",
                "destination": "b/",
                "uname": "b"
            },
            {
                "source": "a/",
                "destination": "d"
            }
        ], directories)

    def test_update_links(self):
        cc = ConstrictorConfiguration({})

        cc.update_configuration({
            "links": [
                {
                    "source": "a",
                    "destination": "b",
                },
                {
                    "source": "c",
                    "destination": "d"
                }
            ]
        })

        cc.update_configuration({
            "links": [
                {
                    "source": "a",
                    "destination": "f",
                },
                {
                    "source": "b",
                    "destination": "d"
                }
            ]
        })

        links = cc['links']

        self.assertEqual([
            {
                "source": "c",
                "destination": "d"
            },
            {
                "source": "a",
                "destination": "f"
            },
            {
                "source": "b",
                "destination": "d"
            }
        ], links)

    def test_update_maintainer_scripts(self):
        cc = ConstrictorConfiguration({})

        cc.update_configuration({
            "maintainer_scripts": {
                "postinst": "postinst1",
                "prerm": "prerm1"
            }
        })

        cc.update_configuration({
            "maintainer_scripts": {
                "postinst": "postinst2",
                "preinst": "preinst2",
            }
        })

        self.assertEqual({
            "postinst": "postinst2",
            "preinst": "preinst2",
            "prerm": "prerm1"
        }, cc['maintainer_scripts'])
