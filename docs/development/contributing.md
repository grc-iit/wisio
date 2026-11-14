# Contributing

The canonical contributor guide is
[`CONTRIBUTING.md`](https://github.com/grc-iit/wisio/blob/main/CONTRIBUTING.md)
in the repository root. This page adds the details that are specific to
building and testing the documentation.

## Development environment

### Dev container (recommended)

The repository includes `.devcontainer.json` and a `Dockerfile` with the
C++/Arrow/HDF5/MPI dependencies. Open the repository in VS Code and choose
**Reopen in Container**, then:

```bash
python -m pip install --upgrade pip
pip install -e .[darshan,dftracer]
pip install -r tests/requirements.txt
```

### Manual setup

```bash
git clone https://github.com/grc-iit/wisio.git
cd wisio
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip meson-python setuptools wheel
pip install -e .[darshan,dftracer]
pip install -r tests/requirements.txt
```

Native dependencies for the C++ components are listed in the
`Install system dependencies` step of
[`.github/workflows/ci.yml`](https://github.com/grc-iit/wisio/blob/main/.github/workflows/ci.yml).
The Spack environment in `tools/spack.yaml` is an alternative.

## Tests

```bash
# Fast smoke tier (default on pushes)
pytest -m smoke --verbose

# Full matrix (release tags and manual runs)
pytest -m full --verbose

# A single file
pytest tests/test_analysis.py -v
```

The C++ components are built and tested with Meson:

```bash
meson build --prefix=$HOME/.local --reconfigure \
  -Denable_tests=true -Denable_tools=true
meson compile -C build --verbose
meson test -C build --verbose
meson test -C build --verbose --setup=mpi
```

End-to-end CLI checks (the same ones CI runs):

```bash
wisio +analyzer=dftracer percentile=0.99 trace_path=tests/data/extracted/dftracer-posix
wisio +analyzer=dftracer percentile=0.99 trace_path=tests/data/extracted/dftracer-dlio
wisio +analyzer=recorder percentile=0.99 trace_path=tests/data/extracted/recorder-parquet
```

Test data is extracted automatically by `tests/conftest.py` into
`tests/data/extracted/` when the suite starts.

## Linting and formatting

WisIO uses Ruff with a 119-character line length and preserved quote style:

```bash
ruff check .
ruff format .
```

## Building the documentation

The docs build is independent of the WisIO runtime. Use a separate virtual
environment so Sphinx dependencies do not mix with the dev environment:

```bash
python -m venv venv-docs
source venv-docs/bin/activate        # Windows: venv-docs\Scripts\Activate.ps1
pip install -r docs/requirements.txt

# One-shot build; warnings are errors.
sphinx-build -b html -W --keep-going docs docs/_build/html

# Or through the Makefile / make.bat
make -C docs html
docs\make.bat html                  # Windows
```

Preview the result:

```bash
python -m http.server -d docs/_build/html 8000
# open http://localhost:8000
```

For live reload while editing:

```bash
pip install sphinx-autobuild
make -C docs livehtml
```

```{note}
Most diagrams are Mermaid fences rendered by the browser from a CDN, so an
internet connection is needed to see them in the preview. The architecture
overview is a committed SVG and always renders.
```

## Documentation style

- Write in MyST Markdown (`.md`); use `{doc}` roles for cross-page links.
- Use fenced code blocks with a language (`bash`, `python`, `text`, `json`).
- Prefer task-oriented sections and copy-pasteable commands.
- Keep the source tree as the source of truth: if a default or a rule changes
  in `wisio/config.py` or `wisio/rules.py`, update the matching page.
- The build must be warning-free (`-W`), including unresolved references.
- Do not document features that are not implemented. If a code path is
  known-broken, open an issue rather than describing it as supported.

## Publishing

The site is hosted on Read the Docs at
<https://wisio.readthedocs.io/>. The build is configured by
[`.readthedocs.yaml`](https://github.com/grc-iit/wisio/blob/main/.readthedocs.yaml):

- Ubuntu 24.04, Python 3.12
- `docs/requirements.txt`
- `docs/conf.py`
- `fail_on_warning: true`

Read the Docs builds `main` as `latest` and tags as versions. Enable **Build
pull requests** in the project settings to get a preview for documentation PRs.

## Pull request checklist

- [ ] `ruff check .` is clean.
- [ ] New behavior has tests; `pytest -m smoke` passes.
- [ ] `sphinx-build -b html -W --keep-going docs docs/_build/html` is clean.
- [ ] New configuration keys, rules, or characteristics are documented.
- [ ] Links to the old `grc.iit.edu/docs/category/wisio/` site are not
      introduced.
