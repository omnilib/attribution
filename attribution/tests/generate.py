# Copyright Amethyst Reese
# Licensed under the MIT license

from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from .. import generate
from ..project import Project
from ..tag import Tag
from ..types import Version

FAKE_CARGO_TOML = """
[package]
name = "fluffy"
version = "1.0"
edition = "2038"

[dependencies]
dog = "3.1"
"""

FAKE_CARGO_LOCK = """
version = 3

[[package]]
name = "dog"
version = "3.1"

[[package]]
name = "fluffy"
version = "1.0"
dependencies = [
 "dog",
]

[[package]]
name = "something"
version = "2.0"
"""


class GenerateTest(TestCase):
    def test_cargo_file(self):
        with TemporaryDirectory() as td:
            tdp = Path(td)
            (cargo_toml := tdp / "Cargo.toml").write_text(FAKE_CARGO_TOML)
            (cargo_lock := tdp / "Cargo.lock").write_text(FAKE_CARGO_LOCK)
            (tdp / "subdir" / "whatever").mkdir(parents=True)
            (tdp / "subdir" / "whatever" / "Cargo.toml").write_text(
                FAKE_CARGO_TOML.replace('name = "fluffy"', 'name = "whatever"')
            )

            project = Project(
                "fluffy",
                "fluffy",
                root=tdp,
                _tags=[
                    Tag("v2.1.3", Version("2.1.3")),
                    Tag("v1.0", Version("1.0")),
                ],
            )

            with self.subTest("search no cargo_packages"):
                self.assertEqual([], generate.CargoFile.search(project, []))

            with self.subTest("search fluffy"):
                expected = [
                    generate.CargoFile(project, package_name="fluffy", package_dir="."),
                ]
                result = generate.CargoFile.search(project, ["fluffy"])
                self.assertEqual(expected, result)

            with self.subTest("search whatever"):
                expected = [
                    generate.CargoFile(
                        project, package_name="whatever", package_dir="subdir/whatever"
                    ),
                ]
                result = generate.CargoFile.search(project, ["whatever"])
                self.assertEqual(expected, result)

            with self.subTest("search fluffy and whatever"):
                expected = [
                    generate.CargoFile(project, package_name="fluffy", package_dir="."),
                    generate.CargoFile(
                        project, package_name="whatever", package_dir="subdir/whatever"
                    ),
                ]
                result = generate.CargoFile.search(project, ["fluffy", "whatever"])
                self.assertEqual(expected, result)

            with self.subTest("generate fluffy"):
                expected = FAKE_CARGO_TOML.replace(
                    'version = "1.0"', 'version = "2.1.3"'
                )
                result = generate.CargoFile.search(
                    project,
                    cargo_packages=["fluffy"],
                )[0].generate()
                self.assertEqual(expected, result)

            with self.subTest("write fluffy"):
                expected = FAKE_CARGO_TOML.replace(
                    'version = "1.0"', 'version = "2.1.3"'
                )
                result = (
                    generate.CargoFile.search(
                        project,
                        cargo_packages=["fluffy"],
                    )[0]
                    .write()
                    .read_text()
                )
                self.assertEqual(expected, result)

                result = cargo_toml.read_text()
                self.assertEqual(expected, result)

                expected = FAKE_CARGO_LOCK.replace(
                    'version = "1.0"', 'version = "2.1.3"'
                )
                result = cargo_lock.read_text()
                self.assertEqual(expected, result)
