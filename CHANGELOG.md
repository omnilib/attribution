attribution
===========

v1.3.1
------

Bugfix release

* Fix writing __version__.py file when no [tool.attribution] table found (#16)
* More debug logging, send debug output to stderr

```
$ git shortlog -s v1.3.0...v1.3.1
     5	John Reese
```


v1.3.0
------

Feature release

* Added `version_file` option in pyproject.toml to disable writing version.py (#12)
* Added sphinx documentation for the package
* Tested on Python 3.9a (#15)

```
$ git shortlog -s v1.2.0...v1.3.0
    14	John Reese
     6	Mark Rofail
     5	pyup.io bot
```


v1.2.0
------

Feature release:

- Move to subcommands for CLI actions
- `attribution generate` will now generate the CHANGELOG content
- Can pull project name from pyproject.toml (`tool.attribution.name`)
- Added `tag` command to bump `__version__`, generate commit, changelog, and tag

```
$ git shortlog -s v1.1...v1.2.0
    13	John Reese
```


v1.1
----

Bugfix release

- Fix install_requires to correctly list attrs and jinja2

```
$ git shortlog -s v1.0...v1.1
     5	John Reese
```


v1.0
----

Initial release

- Generates changelog from git tags with hardcoded template and format

```
$ git shortlog -s v0.0...v1.0
     1	John Reese
```


v0.0
----

Placeholder release

- Name claimed on Github!

```
$ git shortlog -s 7441e33a9326e9c3e567600a0eda9732b259b833...v0.0
     1	John Reese
```

