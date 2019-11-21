# Copyright 2019 John Reese
# Licensed under the MIT license

import logging
import re
import shlex
import subprocess
from typing import List, Match

import click
from jinja2 import Template

from .types import InvalidVersion, Tag, Version

LOG = logging.getLogger(__name__)

GIT_TAG_RE = re.compile(
    r"object\s+(\w+)\ntype\s+(\w+)\ntag\s+(.+)\ntagger\s(.+)\n\n((?s:.*))$"
)
PGP_MSG_RE = re.compile(
    r"-----BEGIN PGP SIGNATURE-----.+-----END PGP SIGNATURE-----\n", re.DOTALL
)

TEMPLATE = Template(
    """
{{- project }}
{{ "=" * len(project) }}
{% for tag in tags %}
{{ tag.name }}
{{ "-" * len(tag.name) }}

{{ tag.message if tag.message else "" }}
{{ tag.shortlog if tag.shortlog else "" }}

{% endfor -%}
"""
)


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


def git_tag_message(tag: Tag) -> Tag:
    """Given a tag object, retrieve its message and any PGP signature."""
    out = sh(f"git cat-file tag {tag.name}")

    match = GIT_TAG_RE.match(out)
    if not match:
        LOG.warning(f"unmatched tag contents for {tag.name}")
        LOG.debug(out)
        return tag

    def pgp(match: Match) -> str:
        tag.signature = match.group(0)
        return ""

    content = match.group(5)
    content = PGP_MSG_RE.sub(pgp, content)
    tag.message = content
    return tag


def git_shortlog(tag: Tag) -> Tag:
    """Given a tag object, generate the associated shortlog."""
    try:
        base = sh(f"git describe --tags --abbrev=0 --always {tag.name}~1").strip()
        cmd = f"git shortlog -s {base}...{tag.name}"
        out = sh(cmd).rstrip()
        tag.shortlog = f"```\n$ {cmd}\n{out}\n```"

    except subprocess.CalledProcessError:
        LOG.exception(f"failed to generate shortlog for {tag.name}")

    return tag


def git_tags() -> List[Tag]:
    """Generate an ordered list of tag objects"""
    names = [n.strip() for n in sh("git tag").splitlines() if n]
    tags: List[Tag] = []
    for name in names:
        try:
            tags.append(Tag(name=name, version=Version(name)))
        except InvalidVersion:
            LOG.warning(f"Skipping tag {name}")

    tags.sort(reverse=True)
    for tag in tags:
        git_tag_message(tag)
        git_shortlog(tag)

    return tags


def generate_from_git(project: str) -> None:
    tags = git_tags()
    output = TEMPLATE.render(project=project, tags=tags, len=len)
    click.echo(output)
