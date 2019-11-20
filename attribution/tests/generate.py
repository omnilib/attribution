# Copyright 2019 John Reese
# Licensed under the MIT license

import subprocess
from unittest import TestCase
from unittest.mock import patch, call

from attr import evolve

from .. import generate as gen
from ..types import Tag, Version, InvalidVersion


class GenerateTest(TestCase):
    def test_sh(self):
        output = gen.sh("echo", "foo bar")
        self.assertEqual(output, "foo bar\n")

    def test_sh_split(self):
        output = gen.sh("echo foo bar")
        self.assertEqual(output, "foo bar\n")

    def test_sh_false(self):
        with self.assertRaisesRegex(
            subprocess.CalledProcessError, "non-zero exit status 1"
        ):
            gen.sh("false")

    @patch("attribution.generate.LOG")
    @patch("attribution.generate.sh")
    def test_git_tag_message(self, sh_mock, log_mock):
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

        tag = Tag("v1.0", Version("1.0"))

        result = gen.git_tag_message(evolve(tag))
        sh_mock.assert_called_with("git cat-file tag v1.0")
        self.assertEqual(result.message, "Tag subject\n\nFoo Bar\n")
        self.assertEqual(
            result.signature,
            "-----BEGIN PGP SIGNATURE-----\n"
            "lotsa gobbledy gook\n"
            "-----END PGP SIGNATURE-----\n",
        )

        result = gen.git_tag_message(evolve(tag))
        log_mock.warning.assert_not_called()
        self.assertEqual(result.message, "Different subject\n")
        self.assertIsNone(result.signature)

        result = gen.git_tag_message(evolve(tag))
        log_mock.warning.assert_called_once()
        self.assertIsNone(result.message)
        self.assertIsNone(result.signature)

    @patch("attribution.generate.LOG")
    @patch("attribution.generate.sh")
    def test_git_tag_shortlog(self, sh_mock, log_mock):
        sh_mock.side_effect = [
            "v0.5\n",
            "shortlog for v0.5\n",
            subprocess.CalledProcessError(1, ()),
        ]

        tag = Tag("v1.0", Version("1.0"))
        result = gen.git_shortlog(evolve(tag))
        sh_mock.assert_has_calls(
            [
                call("git describe --tags --abbrev=0 --always v1.0~1"),
                call("git shortlog -s v0.5...v1.0"),
            ]
        )
        log_mock.exception.assert_not_called()
        self.assertEqual(
            result.shortlog,
            "```\n$ git shortlog -s v0.5...v1.0\nshortlog for v0.5\n```",
        )

        sh_mock.reset_mock()
        result = gen.git_shortlog(evolve(tag))
        sh_mock.assert_called_with("git describe --tags --abbrev=0 --always v1.0~1")
        log_mock.exception.assert_called_once()
        self.assertIsNone(result.shortlog)

    @patch("attribution.generate.LOG")
    @patch("attribution.generate.sh")
    @patch("attribution.generate.git_tag_message")
    @patch("attribution.generate.git_shortlog")
    def test_git_tags(self, shortlog_mock, message_mock, sh_mock, log_mock):
        sh_mock.return_value = "v0.0\nv0.5\nv1.0\nfeature-branch\nv1.1\nv1.2\n"
        expected = [
            Tag("v1.2", Version("1.2")),
            Tag("v1.1", Version("1.1")),
            Tag("v1.0", Version("1.0")),
            Tag("v0.5", Version("0.5")),
            Tag("v0.0", Version("0.0")),
        ]
        result = gen.git_tags()
        sh_mock.assert_called_with("git tag")
        log_mock.warning.assert_called_with("Skipping tag feature-branch")
        self.assertEqual(result, expected)

    @patch("attribution.generate.click")
    @patch("attribution.generate.git_tags")
    @patch("attribution.generate.TEMPLATE")
    def test_generate_from_git(self, tpl_mock, tags_mock, click_mock):
        tags = object()
        output = object()
        tags_mock.return_value = tags
        tpl_mock.render.return_value = output

        gen.generate_from_git("fake name")
        tags_mock.assert_called_with()
        tpl_mock.render.assert_called_with(project="fake name", tags=tags, len=len)
        click_mock.echo.assert_called_with(output)


