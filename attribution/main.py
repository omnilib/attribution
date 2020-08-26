# Copyright 2020 John Reese
# Licensed under the MIT license

import logging

import click

from attribution import __author__, __version__

from .generate import Changelog
from .project import Project


@click.group()
@click.version_option(__version__, "-V", "--version", prog_name="attribution")
@click.option("-d", "--debug", is_flag=True, help="enable debug logging")
def main(debug: bool = False) -> None:
    """Generate changelogs from tags and shortlog"""
    logging.basicConfig(level=logging.DEBUG if debug else logging.WARNING)


@main.command("generate")
def generate() -> None:
    """Regenerate changelog from existing tags"""
    project = Project.load()
    Changelog(project).generate()


@main.command("tag")
def tag() -> None:
    """Create new tagged version with changelog"""


if __name__ == "__main__":
    main(prog_name="attribution")  # pylint: disable=unexpected-keyword-arg
