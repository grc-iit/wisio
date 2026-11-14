# Changelog

Release notes live with the releases on GitHub:

- [WisIO releases](https://github.com/grc-iit/wisio/releases)
- [PyPI version history](https://pypi.org/project/wisio/#history)

## Versioning

WisIO follows `MAJOR.MINOR.PATCH` tags (`v*.*.*`). The documentation version
shown in the Read the Docs flyout is read from `pyproject.toml`, so the site
and the package always report the same version.

- `latest` tracks `main`.
- Release tags are built as separate Read the Docs versions.
- Patch releases (for example `0.2.3`) are documentation-compatible; minor
  releases may add or change configuration keys.

```{note}
WisIO is pre-1.0. Configuration keys and CLI flags are the most stable
surface; the Python API may change between minor releases.
```
