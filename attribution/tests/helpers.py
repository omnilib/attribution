# Copyright 2020 John Reese
# Licensed under the MIT license

import subprocess
from unittest import TestCase

from .. import helpers


class HelpersTest(TestCase):
    def test_sh(self):
        output = helpers.sh("echo", "foo bar")
        self.assertEqual(output, "foo bar\n")

    def test_sh_split(self):
        output = helpers.sh("echo foo bar")
        self.assertEqual(output, "foo bar\n")

    def test_sh_false(self):
        with self.assertRaisesRegex(
            subprocess.CalledProcessError, "non-zero exit status 1"
        ):
            helpers.sh("false")
