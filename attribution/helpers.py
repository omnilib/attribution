# Copyright 2022 Amethyst Reese
# Licensed under the MIT license

import logging
import shlex
import subprocess

from packaging.utils import canonicalize_name

LOG = logging.getLogger(__name__)


def sh(*cmd: str, raw: bool = False) -> str:
    """Run a simple command and return mixed stdout/stderr; raise on non-zero exit"""
    if len(cmd) == 1:
        cmd = tuple(shlex.split(cmd[0]))
    LOG.debug(f"running $ {' '.join(shlex.quote(c) for c in cmd)}")
    try:
        if raw:
            p = subprocess.run(
                cmd,
                check=True,
                encoding="utf-8",
            )
        else:
            p = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=True,
                encoding="utf-8",
            )
        return p.stdout
    except subprocess.CalledProcessError as e:
        LOG.debug(
            f"exit code: {e.returncode}\nstdout:\n{e.stdout}\nstderr:\n{e.stderr}"
        )
        raise


def canonical_namespace(name: str) -> str:
    cname = canonicalize_name(name)
    return cname.replace("-", "_")
