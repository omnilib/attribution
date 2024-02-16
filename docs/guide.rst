User Guide
==========

Commands
--------

attribution has multiple commands broken into two categories: info commands
that display project state to the user, and actions that modify project state
or configuration.

Actions
^^^^^^^

.. attribute:: init

    Initialize configuration for a new project, with interactive prompts.
    Writes or updates the ``[tool.attribution]`` table in your project's
    ``pyproject.toml`` with any chosen configuration options.

    .. code-block:: shell-session

        $ attribution init
        Project name [project]:
        Package namespace [project]:
        Use __version__.py file [Y/n]:
        Use GPG signed tags [Y/n]:

.. attribute:: tag

    Create a new, tagged release. This process automates the following steps:

    - Prompt the user for a changelog entry
    - Write the updated ``CHANGELOG``
    - Write the updated :attr:`version file <version_file>`
    - Create a "version bump" commit
    - Created an annotated (or :attr:`signed <signed_tags>`) tag from that commit

Info
^^^^

.. attribute:: log

    Print a log of revisions since the last tagged version, from oldest to
    newest. This is the same revision log presented to the user when
    :attr:`tagging a new release <tag>`.

    **Experimental:** :attr:`Ignored authors <ignored_authors>` are automatically
    filtered from the resulting output.

    .. code-block:: shell-session

        $ attribution log
        commit 77315cfffd0b67037740463d0588e947d16d6e53
        Author: Amethyst Reese <amy@n7.gg>
        Date:   Sun Sep 11 00:06:11 2022 -0700

            Better theme from ufmt

        commit e1c44e46720253070ade5eb6f35d2a160e7b6fc5 (upstream/main, main)
        Author: Amethyst Reese <amy@n7.gg>
        Date:   Sun Sep 11 00:21:46 2022 -0700

            Basic documentation for commands

        ...

.. attribute:: debug

    Prints debug information about your project and configuration.

    .. code-block:: shell-session

        $ attribution debug
        pyproject.toml: /home/user/project/pyproject.toml
        Project(
            name='Project',
            package='project',
            config={'ignored_authors': [], 'version_file': True, 'signed_tags': True, 'name': 'Project', 'package': 'project'},
            _shortlog=None,
            _tags=[]
        )


Configuration
-------------

All configuration for attribution is done via the :file:`pyproject.toml` file.
This ensures that all maintainers for your project are using a shared
configuration when generating the changelog or tagging new releases.

Specifying options requires adding them to the ``tool.attribution`` namespace,
following this example:

.. code-block:: toml

    [tool.attribution]
    name = "Project"
    package = "project"
    ignored_authors = ["dependabot"]
    signed_tags = true
    version_file = true

These options can be added automatically by running ``attribution init`` from
the root of your project.

Options available are described as follows:

.. attribute:: name
    :type: str

    Specifies the project name that will be used at the top of the changelog,
    and anywhere else the project name is displayed. Defaults to the name
    of the current working directory.

.. attribute:: package
    :type: str

    Specifies the package namespace for your project. This is used when
    creating or updating the package's version file (if :attr:`version_file`
    is ``true``), and should match the top-level namespace used when importing
    your package at runtime.

.. attribute:: cargo_packages
    :type: list[str]
    :value: []

    **Experimental:**
    List of cargo package names that should have their associated ``Cargo.toml``
    and ``Cargo.lock`` files updated when tagging a new release version.

    This can be helpful for PyO3 projects to ensure that cargo versions are
    kept in sync with python project metadata.

    **Note:** this is simple TOML file editing, does not trigger any usage
    of the ``cargo`` binary, and may not be appropriate for use with every
    Rust project.

.. attribute:: ignored_authors
    :type: str | list[str]
    :value: []

    **Experimental:**
    List of author names (or patterns) that will be ignored and excluded when
    showing project revisions. For example, when tagging a new release, any
    configured authors will be excluded from the list of revisions displayed
    as part of the message template.

    This can be helpful for excluding noisy or frequent commits from automated
    sources that aren't likely to be relevant when writing release notes.

    **Note:** this feature currently requires your ``git`` binary be compiled
    with ``USE_LIBPCRE`` support. You can test this availability by running
    ``git log --perl-regexp --author=dependabot``.

.. attribute:: signed_tags
    :type: bool
    :value: True

    Specifies if attribution will use GPG signed tags for git when creating
    and tagging new versions.

.. attribute:: version_file
    :type: bool
    :value: True

    Specifies if attribution should create or update a ``__version__.py`` file
    when initializing the project or tagging new versions. This enables the
    option of importing and setting the common ``__version__`` string value
    from a generated file at runtime, rather than needing to update the
    version string in multiple places:

    .. code-block:: python3
        :caption: project/__version__.py:

        # generated by attribution
        __version__ = "1.2.3"

    .. code-block:: python3
        :caption: project/__init__.py:

        from .__version__ import __version__

        ...

    For projects using mechanisms like :mod:`setuptools_scm`, or that prefer
    to not have a managed ``__version__.py`` file, this value should be set to
    ``false``.
