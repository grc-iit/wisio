"""Sphinx configuration for the WisIO documentation.

The site is built with Sphinx, the Read the Docs theme, and MyST Markdown.
It is intentionally self-contained: importing the `wisio` package here would
pull in Dask, Hydra, and the optional trace readers, so the Python API page is
curated by hand instead of generated with autodoc.
"""

from pathlib import Path
import tomllib

ROOT = Path(__file__).resolve().parents[1]

# The package version is the documentation version. Reading it from
# pyproject.toml keeps the RTD version flyout in sync with releases without a
# second place to bump.
with (ROOT / "pyproject.toml").open("rb") as handle:
    PYPROJECT = tomllib.load(handle)

project = "WisIO"
author = (
    "Izzet Yildirim, Hariharan Devarajan, Anthony Kougkas, "
    "Xian-He Sun, and Kathryn Mohror"
)
copyright = "2024–present, Gnosis Research Center, Illinois Tech"
version = PYPROJECT["project"]["version"]
release = version

# -- General configuration ---------------------------------------------------

extensions = [
    "myst_parser",
    "sphinx_copybutton",
    "sphinx_design",
    "sphinxcontrib.mermaid",
]

source_suffix = {
    ".md": "markdown",
    ".rst": "restructuredtext",
}
root_doc = "index"

# README.md holds maintainer notes (local preview, RTD onboarding) rather than
# site content, so keep it out of the build.
exclude_patterns = ["README.md", "_build", "Thumbs.db", ".DS_Store"]

# -- MyST ---------------------------------------------------------------------

myst_enable_extensions = [
    "attrs_inline",
    "colon_fence",
    "deflist",
    "fieldlist",
    "substitution",
    "tasklist",
]
myst_heading_anchors = 3
myst_substitutions = {
    "version": version,
}

# -- Mermaid ------------------------------------------------------------------

# sphinxcontrib-mermaid renders diagrams in the browser. Pinning the major
# version keeps the generated HTML stable across builds.
mermaid_version = "11"

# -- HTML output --------------------------------------------------------------

html_theme = "sphinx_rtd_theme"
html_title = "WisIO Documentation"
html_short_title = "WisIO"
html_baseurl = "https://wisio.readthedocs.io/en/latest/"

html_theme_options = {
    "logo_only": True,
    "prev_next_buttons_location": "bottom",
    "style_external_links": True,
    # Supported Read the Docs theme option: any valid CSS background value.
    # This is the WisIO red sampled from assets/logo.png (#D31F30).
    "style_nav_header_background": "#d31f30",
    "collapse_navigation": False,
    "sticky_navigation": True,
    "navigation_depth": 4,
    "includehidden": True,
    "titles_only": False,
    "version_selector": True,
    "language_selector": True,
}

html_static_path = ["_static"]
templates_path = ["_templates"]
html_css_files = ["css/wisio.css"]
# The sidebar header is WisIO red, so the wordmark is the white variant.
html_logo = "_static/img/wisio-logo-white.png"
html_favicon = "_static/img/favicon.png"

# "Edit on GitHub" / "View source" links in the breadcrumb bar.
html_context = {
    "display_github": True,
    "github_user": "grc-iit",
    "github_repo": "wisio",
    "github_version": "main",
    "conf_py_path": "/docs/",
}

htmlhelp_basename = "wisiodoc"

# -- Link checking ------------------------------------------------------------

# These sites reject automated link checkers or require JavaScript, so they are
# not useful signals for a documentation build.
linkcheck_ignore = [
    r"https://doi\.org/.*",
    r"https://wisio-web\.streamlit\.app/.*",
    r"https://deepwiki\.com/.*",
]
