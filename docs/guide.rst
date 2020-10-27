User Guide
==========

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

Options available are described as follows:

.. attribute:: name

    Specifies the project name that will be used at the top of the changelog,
    and anywhere else the project name is displayed. Defaults to the name
    of the current working directory.

.. attribute:: version_file

    Boolean value [true/false] that specifies if the `Attribute` should add the file
    `__version__.py` to the repo. Some projects are already using something like
    `setuptools_scm` to manage version info, so it maybe redundant.
