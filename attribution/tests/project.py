# Copyright 2020 John Reese
# Licensed under the MIT license

import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

from ..project import Project
from ..tag import Tag, Version


class ProjectTest(TestCase):
    def test_project_eq(self):
        p1 = Project("foo")
        p2 = Project("bar")
        p3 = Project("foo")
        not_project = 42

        self.assertIsNot(p1, p2)
        self.assertNotEqual(p1, p2)

        self.assertIsNot(p1, p3)
        self.assertEqual(p1, p3)

        self.assertNotEqual(p1, not_project)

    @patch("attribution.project.Tag")
    def test_tags(self, tag_mock):
        fake_tags = [
            Tag(name="v1.0", version=Version("1.0")),
            Tag(name="v1.1", version=Version("1.1")),
        ]
        tag_mock.all_tags.return_value = fake_tags

        project = Project(name="foo", config={})
        result = project.tags
        tag_mock.all_tags.assert_called_once()
        self.assertEqual(result, fake_tags)

        tag_mock.all_tags.reset_mock()
        result = project.tags
        tag_mock.all_tags.assert_not_called()
        self.assertEqual(result, fake_tags)

    @patch("attribution.project.LOG")
    @patch("attribution.project.sh")
    def test_shortlog(self, sh_mock, log_mock):
        sh_mock.side_effect = [
            "  10 Foo Bar\n",
            subprocess.CalledProcessError(1, ()),
        ]

        project = Project("foo")
        result = project.shortlog
        sh_mock.assert_called_with(project.shortlog_cmd)
        self.assertEqual(result, "  10 Foo Bar")

        # cached value
        sh_mock.reset_mock()
        result = project.shortlog
        sh_mock.assert_not_called()
        self.assertEqual(result, "  10 Foo Bar")

        sh_mock.reset_mock()
        project = Project("foo")
        result = project.shortlog
        sh_mock.assert_called_with(project.shortlog_cmd)
        log_mock.exception.assert_called_once()
        self.assertEqual(result, "")

    @patch("attribution.project.Path.cwd")
    def test_load(self, cwd_mock):
        fake_pyproject = """
[tool.attribution]
name = "fizzbuzz"
        """

        with TemporaryDirectory() as td:
            td = Path(td)
            pyproject = td / "pyproject.toml"
            pyproject.write_text(fake_pyproject.strip())
            cwd_mock.return_value = td

            with self.subTest("pyproject in cwd"):
                project = Project.load()
                cwd_mock.assert_called_once()
                self.assertEqual(project.name, "fizzbuzz")
                self.assertEqual(
                    project.config, {"name": "fizzbuzz", "version_file": True}
                )
                cwd_mock.reset_mock()

            with self.subTest("pyproject in given path"):
                project = Project.load(td)
                cwd_mock.assert_not_called()
                self.assertEqual(project.name, "fizzbuzz")
                self.assertEqual(
                    project.config, {"name": "fizzbuzz", "version_file": True}
                )

            with self.subTest("pyproject with no version_file defaults to True"):
                pyproject.write_text(fake_pyproject.strip())
                project = Project.load(td)
                self.assertTrue(project.config.get("version_file"))
                self.assertEqual(
                    project.config, {"name": "fizzbuzz", "version_file": True}
                )

            with self.subTest("pyproject reads version_file"):
                pyproject.write_text(fake_pyproject.strip() + "\nversion_file=false")
                project = Project.load(td)
                self.assertFalse(project.config.get("version_file"))
                self.assertEqual(
                    project.config, {"name": "fizzbuzz", "version_file": False}
                )

            with self.subTest("empty pyproject"):
                pyproject.write_text("\n")
                project = Project.load(td)
                cwd_mock.assert_not_called()
                self.assertEqual(project.name, td.name)
                self.assertEqual(project.config, {"version_file": True})

            with self.subTest("no pyproject"):
                pyproject.unlink()
                project = Project.load(td)
                cwd_mock.assert_not_called()
                self.assertEqual(project.name, td.name)
                self.assertEqual(project.config, {"version_file": True})
