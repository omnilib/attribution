# Copyright 2020 John Reese
# Licensed under the MIT license

import logging
import os
from pathlib import Path

import click

from attribution import __author__, __version__

from .generate import Changelog, Contributers
from .project import Project
from .tag import Tag


@click.command(name="attribution", help="generate changelogs from tags and shortlog")
@click.version_option(__version__, "-V", "--version", prog_name="attribution")
@click.option("-d", "--debug", is_flag=True, help="enable debug logging")
def main(debug: bool = False) -> None:
    logging.basicConfig(level=logging.DEBUG if debug else logging.WARNING)

    name = Path(os.getcwd()).name

    project = Project(name)
    tags = Tag.all_tags()
    Changelog(project).generate(tags)
    Contributers(project).generate(tags)


if __name__ == "__main__":
    main()
