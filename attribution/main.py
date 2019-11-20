# Copyright 2019 John Reese
# Licensed under the MIT license

import click

from attribution import __author__, __version__


@click.command(name="attribution", help="generate changelogs from tags and shortlog")
@click.version_option(version=__version__, prog_name="attribution")
def main():
    pass


if __name__ == "__main__":
    main()
