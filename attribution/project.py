# Copyright 2020 John Reese
# Licensed under the MIT license

import logging
import subprocess
from typing import Any, Optional

from attr import dataclass

from .helpers import sh

LOG = logging.getLogger(__name__)


@dataclass(eq=False)
class Project:
    name: str
    _shortlog: Optional[str] = None

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Project):
            return self.name == other.name
        return False

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
