# Copyright 2022 Amethyst Reese
# Licensed under the MIT license

import logging
import sys
from pathlib import Path
from typing import Any, Callable, Optional

import click
import tomlkit

from attribution import __version__
from .generate import Changelog, VersionFile
from .helpers import sh
from .project import Project
from .tag import Tag
from .types import Version

LOG = logging.getLogger(__name__)


@click.group()
@click.version_option(__version__, "-V", "--version", prog_name="attribution")
@click.option("-d", "--debug", is_flag=True, help="Enable debug logging")
def main(debug: bool = False) -> None:
    """Generate changelogs from tags and shortlog"""
    logging.basicConfig(
        level=logging.DEBUG if debug else logging.WARNING, stream=sys.stderr
    )


@main.command("init")
def init() -> None:
    project = Project.load()
    name = click.prompt("Project name", default=project.name)
    package = click.prompt("Package namespace", default=project.package)
    version_file = click.confirm(
        "Use __version__.py file", default=project.config["version_file"]
    )
    signed_tags = click.confirm(
        "Use GPG signed tags", default=project.config["signed_tags"]
    )

    if project.pyproject_path().is_file():
        pyproject = tomlkit.loads(project.pyproject_path().read_text())
        add_newline = True
    else:
        pyproject = tomlkit.document()
        add_newline = False

    tool = pyproject.get("tool", None)
    if tool is None:
        if add_newline:
            pyproject.append(None, tomlkit.nl())
        tool = tomlkit.table()
        # gross, but prevents a blank [tool] table
        tool._is_super_table = True
        pyproject.append("tool", tool)

    table = tool.get("attribution", None)
    if table is None:
        table = tomlkit.table()
        tool.append("attribution", table)

    table["name"] = name
    table["package"] = package
    table["signed_tags"] = signed_tags
    table["version_file"] = version_file

    project.pyproject_path().write_text(tomlkit.dumps(pyproject))

    # pick up any changes
    project = Project.load()
    if version_file:
        VersionFile(project).write()


@main.command("debug")
def debug() -> None:
    """Dump debug info about project"""
    pprint: Callable[[Any], None]
    try:
        import rich

        pprint = rich.print
    except ImportError:
        pprint = click.echo

    project = Project.load()
    pprint(f"pyproject.toml: {project.pyproject_path()}")
    pprint(project)


@main.command("log")
def show_log() -> None:
    """Show log of revisions since last tag"""
    project = Project.load()
    if project.tags:
        tag = project.tags[0]
        log_cmd = ["git", "log", "--reverse", f"{tag.name}.."]
    else:
        log_cmd = ["git", "log", "--reverse"]

    log_cmd += ["--invert-grep"]
    for author in project.config["ignored_authors"]:
        log_cmd += [f"--author={author}"]
    sh(*log_cmd, raw=True)


@main.command("generate")
def generate() -> None:
    """Regenerate changelog from existing tags"""
    project = Project.load()
    LOG.debug(f"project: {project}")
    click.echo(Changelog(project).generate())


@main.command("tag")
@click.option(
    "-m",
    "--message",
    type=str,
    default=None,
    help="Use the given message instead of prompting",
)
@click.argument("version", type=Version)
def tag_release(version: Version, message: Optional[str]) -> None:
    """Create new tagged release with changelog"""
    project = Project.load()
    LOG.debug(f"project: {project}")

    for tag in project.tags:
        if tag.version == version:
            click.secho(f"abort: tag {tag.name!r} already exists!", fg="yellow")
            click.get_current_context().exit(1)

    if message is None:
        tpl = (
            f"\n# Write a changelog for version {version}\n#\n"
            "# Lines starting with '#' will be ignored\n"
        )

        if project.tags:
            tag = project.tags[0]
            log_cmd = ["git", "log", "--reverse", f"{tag.name}..", "--invert-grep"]
            for author in project.config["ignored_authors"]:
                log_cmd += [f"--author={author}"]
            git_log = sh(*log_cmd)
            tpl += f"#\n# Changes since {tag.name}:\n#\n"
            tpl += "".join(f"# {line}\n" for line in git_log.splitlines(keepends=False))

        message = click.edit(tpl)
        if message is None:
            click.echo("No message given, aborting")
            return

        message = "".join(
            line
            for line in message.splitlines(keepends=True)
            if not line.startswith("#")
        )

    try:
        # XXX: This is a really hacky wall of commands
        project = Project.load()
        LOG.debug(f"project: {project}")

        # create empty commit and tag with new version
        sh(f"git commit -m 'Version bump v{version}' --allow-empty")
        tag = Tag.create(version, message=message, signed=False)

        # update changelog and version file
        changelog = Changelog(project).write()
        sh(f"git add {changelog}")
        if project.config.get("version_file"):
            path = VersionFile(project).write()
            sh(f"git add {path}")

        # update commit and tag
        sh("git commit --amend --no-edit")
        tag.update(message=message, signed=project.config["signed_tags"])

    except Exception:
        mfile = Path(f".attribution-{version}.txt").resolve()
        mfile.write_text(message)
        click.secho(
            f"Bump failed, version message in {mfile}, "
            r"repo state unknown ¯\_(ツ)_/¯",
            fg="yellow",
            bold=True,
        )
        raise


if __name__ == "__main__":
    main(prog_name="attribution")
