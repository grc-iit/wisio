# Documentation maintenance

This directory contains the Sphinx/MyST source for
<https://wisio.readthedocs.io/>. It is excluded from the built site.

## Local preview

```bash
python -m venv venv-docs
source venv-docs/bin/activate        # Windows: venv-docs\Scripts\Activate.ps1
pip install -r docs/requirements.txt

sphinx-build -b html -W --keep-going docs docs/_build/html
python -m http.server -d docs/_build/html 8000
```

Open <http://localhost:8000>. On Windows, `docs\make.bat html` does the same
build.

For live reload:

```bash
pip install sphinx-autobuild
make -C docs livehtml
```

## Warnings are errors

The local build and Read the Docs both use `-W`, so treat warnings as failures:

- unresolved `{doc}` / `{ref}` targets,
- documents missing from a toctree,
- duplicate labels,
- malformed table or fence syntax.

## Layout

| Path | Contents |
| --- | --- |
| `index.md` | Landing page and all toctrees |
| `getting-started/` | Installation, first run, trace formats |
| `user-guide/` | CLI, configuration, analysis, rules, outputs, clusters, notebooks, WisIO Web |
| `development/` | Architecture, Python API, contributing |
| `project/` | Paper, FAQ, changelog |
| `_static/css/wisio.css` | Brand overrides for `sphinx_rtd_theme` |
| `_static/img/` | Logo, favicon, architecture diagram |
| `_templates/layout.html` | Suppresses the duplicated site title on the home page |

## Branding

The theme is `sphinx_rtd_theme`. The brand red is `#d31f30`, sampled from
`assets/logo.png`, with `#a8182a` and `#8a1423` as darker variants:

- `html_theme_options["style_nav_header_background"]` colors the sidebar search
  header (a supported theme option).
- `_static/css/wisio.css` overrides links, navigation, inline code, headings,
  tables, and the version badge.
- `wisio-logo-white.png` is used in the red sidebar header;
  `wisio-logo.png` is the red wordmark used on the landing page.

If the logo or brand color changes, regenerate the white sidebar variant and
the square favicon from the new brand asset so they stay in sync. The favicon
is the first `W` glyph cropped from `assets/logo.png` (x=0–65), recolored
white, and centered on a red rounded square.

## Read the Docs setup

The project is configured by `.readthedocs.yaml` at the repository root:

- Ubuntu 24.04, Python 3.12,
- `docs/requirements.txt`,
- `docs/conf.py`,
- `fail_on_warning: true`.

To publish a fork or a new project, import the repository on Read the Docs and
let it detect `.readthedocs.yaml`. Enable **Build pull requests** in the project
settings to get preview builds for documentation PRs.

## Source of truth

The documented defaults, rules, and formulas must match the code:

- configuration: `wisio/config.py`
- rules and characteristics: `wisio/rules.py`
- scoring and severities: `wisio/analysis.py`, `wisio/scoring.py`
- output artifacts: `wisio/output.py`
- CLI wiring: `wisio/__main__.py`
- web app limits: `streamlit_app.py`
- notebook workflow: `notebooks/analysis.ipynb`

If you change one of those, update the matching page in the same PR.
