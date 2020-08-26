attribution
===========

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

