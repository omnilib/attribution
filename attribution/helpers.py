# Copyright 2020 John Reese
# Licensed under the MIT license

import logging
import shlex
import subprocess

LOG = logging.getLogger(__name__)


def sh(*cmd: str) -> str:
    """Run a simple command and return mixed stdout/stderr; raise on non-zero exit"""
    if len(cmd) == 1:
        cmd = tuple(shlex.split(cmd[0]))
    LOG.debug(f"running $ {' '.join(shlex.quote(c) for c in cmd)}")
    p = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=True,
        encoding="utf-8",
    )
    return p.stdout
