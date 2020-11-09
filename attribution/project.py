# Copyright 2020 John Reese
# Licensed under the MIT license

import logging
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional

import tomlkit
from attr import dataclass

from .helpers import sh
from .tag import Tag, Tags

LOG = logging.getLogger(__name__)


@dataclass(eq=False)
class Project:
    name: str
    package: str
    config: Dict[str, Any] = {}
    _shortlog: Optional[str] = None
    _tags: Tags = []

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Project):
            return self.name == other.name and self.package == other.package
        return False

    @property
    def tags(self) -> Tags:
        if not self._tags:
            self._tags = Tag.all_tags()

        return self._tags

    @property
    def latest(self) -> Tag:
        return self.tags[0]

    @property
    def shortlog_cmd(self) -> str:
        """Generate the shortlog command to be run."""
        return "git shortlog -s"

    @property
    def shortlog(self) -> str:
        """Generate the project's combined shortlog."""
        if self._shortlog is None:
            try:
                self._shortlog = sh(self.shortlog_cmd).rstrip()

            except subprocess.CalledProcessError:
                LOG.exception(f"failed to generate shortlog for {self.name}")
                self._shortlog = ""

        return self._shortlog

    @classmethod
    def load(cls, path: Optional[Path] = None) -> "Project":
        if path is None:
            path = Path.cwd()

        # defaults
        name = ""
        package = ""
        config: Dict[str, Any] = {
            "version_file": True,
        }

        if cls.pyproject_path(path).is_file():
            pyproject = tomlkit.loads(cls.pyproject_path(path).read_text())
            if "tool" in pyproject and "attribution" in pyproject["tool"]:
                config.update(pyproject["tool"]["attribution"])
                name = config.get("name", "")
                package = config.get("package", "")

        if not name:
            name = path.name

        if not package:
            package = path.name

        return Project(name=name, package=package, config=config)

    @classmethod
    def pyproject_path(cls, path: Optional[Path] = None) -> Path:
        if path is None:
            path = Path.cwd()

        return path / "pyproject.toml"