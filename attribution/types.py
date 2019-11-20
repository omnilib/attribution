# Copyright 2019 John Reese
# Licensed under the MIT license

from typing import Optional

from attr import dataclass
from packaging.version import Version, InvalidVersion

__all__ = [
    "Tag",
    "InvalidVersion",
    "Version",
]


@dataclass(eq=False)
class Tag:
    name: str
    version: Version
    message: Optional[str] = None
    signature: Optional[str] = None
    shortlog: Optional[str] = None

    def __eq__(self, other):
        if isinstance(other, Tag):
            return self.version == other.version and self.name == other.name
        return False

    def __lt__(self, other):
        if isinstance(other, Tag):
            return self.version < other.version
        raise TypeError

    def __gt__(self, other):
        if isinstance(other, Tag):
            return self.version > other.version
        raise TypeError