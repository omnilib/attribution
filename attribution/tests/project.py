# Copyright 2020 John Reese
# Licensed under the MIT license

import subprocess
from unittest import TestCase
from unittest.mock import patch

from ..project import Project


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
