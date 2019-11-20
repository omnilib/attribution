# Copyright 2019 John Reese
# Licensed under the MIT license

import subprocess
from unittest import TestCase
from unittest.mock import patch, call

from .. import generate as gen
from ..types import Tag, Version, InvalidVersion


class TypesTest(TestCase):
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
        not_tag = 24

        self.assertLess(tag1, tag2)
        self.assertLess(tag1, tag3)
        self.assertLess(tag2, tag3)
        self.assertGreater(tag3, tag2)
        self.assertGreater(tag3, tag1)
        self.assertGreater(tag2, tag1)

    def test_tag_order_other(self):
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

