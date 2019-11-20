# Copyright 2019 John Reese
# Licensed under the MIT license

import click
import logging
import os

from pathlib import Path
from typing import Optional

from attribution import __author__, __version__
from .generate import generate_from_git


@click.command(name="attribution", help="generate changelogs from tags and shortlog")
@click.version_option(version=__version__, prog_name="attribution")
@click.option("-d", "--debug", is_flag=True, help="enable debug logging")
@click.argument("project", type=str, required=False, default=None)
def main(debug: bool, project: Optional[str]) -> None:
    logging.basicConfig(level=logging.DEBUG if debug else logging.WARNING)

    if project is None:
        project = Path(os.getcwd()).name

    generate_from_git(project)


if __name__ == "__main__":
    main()
