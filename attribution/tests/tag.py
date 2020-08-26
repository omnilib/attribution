# Copyright 2020 John Reese
# Licensed under the MIT license

# pylint: disable=protected-access

import subprocess
from unittest import TestCase
from unittest.mock import call, patch

from attr import evolve

from ..tag import Tag
from ..types import Version


class TagTest(TestCase):
    def test_tag_eq(self):
        tag1 = Tag("1.0", Version("1.0"))
        tag2 = Tag("1.0", Version("1.0"))
        tag3 = Tag("v1.0", Version("1.0"))
        not_tag = 24

        self.assertIsNot(tag1, tag2)
        self.assertEqual(tag1, tag2)
        self.assertNotEqual(tag1, tag3)
        self.assertNotEqual(tag1, not_tag)

    def test_tag_order(self):
        tag1 = Tag("v1.0", Version("1.0"))
        tag2 = Tag("v1.1", Version("1.1"))
        tag3 = Tag("v1.2", Version("1.2"))

        self.assertLess(tag1, tag2)
        self.assertLess(tag1, tag3)
        self.assertLess(tag2, tag3)
        self.assertGreater(tag3, tag2)
        self.assertGreater(tag3, tag1)
        self.assertGreater(tag2, tag1)

    def test_tag_order_other(self):
        # pylint: disable=pointless-statement, misplaced-comparison-constant
        tag = Tag("1.0", Version("1.0"))
        with self.assertRaises(TypeError):
            tag < 24

        with self.assertRaises(TypeError):
            tag <= 24

        with self.assertRaises(TypeError):
            24 < tag

        with self.assertRaises(TypeError):
            24 <= tag

        with self.assertRaises(TypeError):
            tag > 24

        with self.assertRaises(TypeError):
            tag >= 24

        with self.assertRaises(TypeError):
            24 > tag

        with self.assertRaises(TypeError):
            24 >= tag

    @patch("attribution.tag.LOG")
    @patch("attribution.tag.sh")
    def test_message(self, sh_mock, log_mock):
        sh_mock.side_effect = [
            (
                "object 123abc\ntype commit\ntag v1.0\ntagger Someone\n\n"
                "Tag subject\n\nFoo Bar\n"
                "-----BEGIN PGP SIGNATURE-----\n"
                "lotsa gobbledy gook\n"
                "-----END PGP SIGNATURE-----\n"
            ),
            (
                "object 123abc\ntype commit\ntag v1.0\ntagger Someone\n\n"
                "Different subject\n"
            ),
            "something weird that should never match",
        ]

        proto = Tag("v1.0", Version("1.0"))

        tag = evolve(proto)
        result = tag.message
        sh_mock.assert_called_with("git cat-file tag v1.0")
        self.assertEqual(result, "Tag subject\n\nFoo Bar\n")
        self.assertEqual(
            tag._signature,
            "-----BEGIN PGP SIGNATURE-----\n"
            "lotsa gobbledy gook\n"
            "-----END PGP SIGNATURE-----\n",
        )

        # cached value
        sh_mock.reset_mock()
        result = tag.message
        sh_mock.assert_not_called()
        self.assertEqual(result, "Tag subject\n\nFoo Bar\n")

        tag = evolve(proto)
        result = tag.message
        log_mock.warning.assert_not_called()
        self.assertEqual(result, "Different subject\n")
        self.assertIsNone(tag._signature)

        tag = evolve(proto)
        result = tag.message
        log_mock.warning.assert_called_once()
        self.assertEqual(result, "")
        self.assertIsNone(tag._signature)

    @patch("attribution.tag.LOG")
    @patch("attribution.tag.sh")
    def test_shortlog(self, sh_mock, log_mock):
        sh_mock.side_effect = [
            "v0.5\n",
            "shortlog for v0.5\n",
            subprocess.CalledProcessError(1, ()),
        ]

        proto = Tag("v1.0", Version("1.0"))

        tag = evolve(proto)
        result = tag.shortlog
        sh_mock.assert_has_calls(
            [
                call("git describe --tags --abbrev=0 --always v1.0~1"),
                call("git shortlog -s v0.5...v1.0"),
            ]
        )
        log_mock.exception.assert_not_called()
        self.assertEqual(result, "shortlog for v0.5")

        # cached values
        sh_mock.reset_mock()
        expected = tag._shortlog_cmd
        result = tag.shortlog_cmd
        self.assertEqual(result, expected)
        result = tag.shortlog
        sh_mock.assert_not_called()
        self.assertEqual(result, "shortlog for v0.5")

        tag = evolve(proto)
        sh_mock.reset_mock()
        result = tag.shortlog
        sh_mock.assert_called_with("git describe --tags --abbrev=0 --always v1.0~1")
        log_mock.exception.assert_called_once()
        self.assertEqual(result, "")

    @patch("attribution.tag.LOG")
    @patch("attribution.tag.sh")
    def test_all_tags(self, sh_mock, log_mock):
        sh_mock.return_value = "v0.0\nv0.5\nv1.0\nfeature-branch\nv1.1\nv1.2\n"
        expected = [
            Tag("v1.2", Version("1.2")),
            Tag("v1.1", Version("1.1")),
            Tag("v1.0", Version("1.0")),
            Tag("v0.5", Version("0.5")),
            Tag("v0.0", Version("0.0")),
        ]
        result = Tag.all_tags()
        sh_mock.assert_called_with("git tag")
        log_mock.warning.assert_called_with("Skipping tag feature-branch")
        self.assertEqual(result, expected)

    @patch("attribution.tag.sh")
    def test_create(self, sh_mock):
        sh_mock.return_value = ""
        expected = Tag("v1.1", Version("1.1"))
        result = Tag.create(Version("1.1"), "Does more stuff")
        sh_mock.assert_called_with(
            "git", "tag", "--annotate", "v1.1", "-m", "Does more stuff"
        )
        self.assertEqual(result, expected)

        result = Tag.create(Version("1.1"), "Does more stuff", signed=True)
        sh_mock.assert_called_with(
            "git", "tag", "--sign", "v1.1", "-m", "Does more stuff"
        )
        self.assertEqual(result, expected)

    @patch("attribution.tag.sh")
    def test_update(self, sh_mock):
        sh_mock.return_value = ""
        tag = Tag("v1.1", Version("1.1"))
        tag._message = "Now with more stuff"

        tag.update()
        sh_mock.assert_called_with(
            "git", "tag", "--force", "--annotate", "v1.1", "-m", "Now with more stuff"
        )
        self.assertEqual(tag._message, "Now with more stuff")

        tag.update(message="Now with even more stuff!", signed=True)
        sh_mock.assert_called_with(
            "git", "tag", "--force", "--sign", "v1.1", "-m", "Now with even more stuff!"
        )
        self.assertIsNone(tag._message)
