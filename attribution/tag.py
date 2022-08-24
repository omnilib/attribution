# Copyright 2022 Amethyst Reese
# Licensed under the MIT license

import logging
import re
import subprocess
from typing import Any, List, Match, Optional

from attr import dataclass

from .helpers import sh
from .types import InvalidVersion, Version

LOG = logging.getLogger(__name__)

GIT_TAG_RE = re.compile(
    r"object\s+(\w+)\ntype\s+(\w+)\ntag\s+(.+)\ntagger\s(.+)\n\n((?s:.*))$"
)
PGP_MSG_RE = re.compile(
    r"-----BEGIN PGP SIGNATURE-----.+-----END PGP SIGNATURE-----\n", re.DOTALL
)


@dataclass(eq=False)
class Tag:
    name: str
    version: Version

    _message: Optional[str] = None
    _signature: Optional[str] = None
    _shortlog_cmd: Optional[str] = None
    _shortlog: Optional[str] = None

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Tag):
            return self.version == other.version and self.name == other.name
        return False

    def __lt__(self, other: Any) -> bool:
        if isinstance(other, Tag):
            return self.version < other.version
        raise TypeError

    def __gt__(self, other: Any) -> bool:
        if isinstance(other, Tag):
            return self.version > other.version
        raise TypeError

    @property
    def message(self) -> str:
        """Retrieve the tag's message and any PGP signature."""
        if self._message is None:
            out = sh(f"git cat-file tag {self.name}")

            match = GIT_TAG_RE.match(out)
            if not match:
                LOG.warning(f"unmatched tag contents for {self.name}")
                LOG.debug(out)
                return ""

            def pgp(match: Match) -> str:
                self._signature = match.group(0)
                return ""

            content = match.group(5)
            content = PGP_MSG_RE.sub(pgp, content)
            self._message = content

        return self._message

    @property
    def shortlog_cmd(self) -> str:
        """Generate the shortlog command to be run."""
        if self._shortlog_cmd is None:
            base = sh(f"git describe --tags --abbrev=0 --always {self.name}~1").strip()

            # If there is no preceding tag, the describe command above will just return
            # the rev hash of the commit preceding the tag, resulting in a bad shortlog.
            # We can use `git tag -l <name>` to see if it's a real tag or just a hash.
            # If it's just a rev, then this is the earliest tag in that tree, and we
            # should just generate a shortlog without a starting ref.
            # To save shell commands, we assume that any Version-like name is a tag.
            try:
                Version(base)
            except InvalidVersion:
                base = sh(f"git tag -l {base}").strip()
            if base:
                spec = f"{base}...{self.name}"
            else:
                spec = self.name

            self._shortlog_cmd = f"git shortlog -s {spec}"

        return self._shortlog_cmd

    @property
    def shortlog(self) -> str:
        """Generate the tag's associated shortlog."""
        if self._shortlog is None:
            try:
                self._shortlog = sh(self.shortlog_cmd).rstrip()

            except subprocess.CalledProcessError:
                LOG.exception(f"failed to generate shortlog for {self.name}")
                self._shortlog = ""

        return self._shortlog

    @classmethod
    def all_tags(cls) -> List["Tag"]:
        """Generate an ordered list of tag objects"""
        names = [n.strip() for n in sh("git tag").splitlines() if n]
        tags: List[Tag] = []
        for name in names:
            try:
                tags.append(Tag(name=name, version=Version(name)))
            except InvalidVersion:
                LOG.warning(f"Skipping tag {name}")

        tags.sort(reverse=True)

        return tags

    @classmethod
    def create(cls, version: Version, message: str, *, signed: bool = False) -> "Tag":
        """Create a new tag with the given message"""
        name = f"v{version}"
        flag = "--sign" if signed else "--annotate"
        sh("git", "tag", flag, name, "-m", message)

        return Tag(name=name, version=version)

    def update(self, message: Optional[str] = None, *, signed: bool = False) -> None:
        """Update an existing tag, reusing the existing message if not given"""
        if message is None:
            message = self.message
        else:
            self._message = None
        flag = "--sign" if signed else "--annotate"
        sh("git", "tag", "--force", flag, self.name, "-m", message)

    @classmethod
    def null(cls):
        # pylint: disable=protected-access
        null_tag = Tag("v0", Version("0"))
        null_tag._message = ""
        null_tag._shortlog = ""
        return null_tag


Tags = List[Tag]
