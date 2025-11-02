# Copyright 2022 Amethyst Reese
# Licensed under the MIT license

import logging
import re
import subprocess
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional, Sequence

import tomlkit

from .helpers import canonical_namespace, sh
from .tag import Tag, Tags
from .types import Version

LOG = logging.getLogger(__name__)


@dataclass
class Project:
    name: str
    package: str
    config: Dict[str, Any] = field(default_factory=dict)
    root: Path = field(default_factory=Path.cwd)
    _shortlog: Optional[str] = field(default=None, compare=False)
    _tags: Tags = field(default_factory=list, compare=False)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Project):
            return self.name == other.name and self.package == other.package
        return False

    @property
    def tags(self) -> Tags:
        if not self._tags:
            self._tags = Tag.all_tags()

        return self._tags

    def get_tag(self, version: Version) -> Optional[Tag]:
        for tag in self.tags:
            if tag.version == version:
                return tag
        return None

    @property
    def latest(self) -> Tag:
        tags = self.tags
        if tags:
            return tags[0]
        else:
            return Tag.null()

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

    def log_since_tag_cmd(self, tag: Optional[Tag] = None) -> Sequence[str]:
        if tag:
            log_cmd = ["git", "log", "--reverse", f"{tag.name}.."]
        else:
            log_cmd = ["git", "log", "--reverse"]

        ignored_authors = self.config.get("ignored_authors", [])
        if ignored_authors:
            inner_pattern = "|".join(
                re.escape(author) for author in self.config["ignored_authors"]
            )
            log_cmd += [
                "--perl-regexp",
                "--regexp-ignore-case",
                rf"--author=^((?!({inner_pattern})).*)$",
            ]

        return log_cmd

    def filter_contributors(self, names: set[str]) -> set[str]:
        if ignored_authors := self.config.get("ignored_authors", []):
            ignore_regex = re.compile(
                "(" + "|".join(re.escape(author) for author in ignored_authors) + ")"
            )
            names = {name for name in names if not ignore_regex.match(name)}
        return names

    @classmethod
    def load(cls, path: Optional[Path] = None) -> "Project":
        if path is None:
            path = Path.cwd()

        # defaults
        name = ""
        package = ""
        config: Dict[str, Any] = {
            "cargo_packages": [],
            "ignored_authors": [],
            "version_file": True,
            "signed_tags": True,
        }

        if cls.pyproject_path(path).is_file():
            pyproject = tomlkit.loads(cls.pyproject_path(path).read_text())
            tool = pyproject.get("tool", {})
            tool_attribution = tool.get("attribution", {})
            if tool_attribution:
                config.update(tool_attribution)
                name = config.get("name", "")
                package = config.get("package", "")
                ignored_authors = config.get("ignored_authors", [])

                if ignored_authors:
                    if isinstance(ignored_authors, str):
                        config["ignored_authors"] = list(ignored_authors)
                    elif isinstance(ignored_authors, list):
                        for author in list(ignored_authors):
                            if not isinstance(author, str):
                                LOG.warning(
                                    f"ignored_authors value {author!r} must be string"
                                )
                                ignored_authors.remove(author)
                    else:
                        LOG.warning("ignored_authors must be string or list of strings")
                        ignored_authors = []
                    config["ignored_authors"] = ignored_authors

        if not name:
            name = path.name

        if not package:
            package = canonical_namespace(path.name)

        return Project(
            name=name,
            package=package,
            config=config,
            root=path,
        )

    @classmethod
    def pyproject_path(cls, path: Optional[Path] = None) -> Path:
        if path is None:
            path = Path.cwd()

        return path / "pyproject.toml"
