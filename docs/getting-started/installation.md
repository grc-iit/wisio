# Installation

```{note}
WisIO requires **Python 3.10 or newer**. The analysis core is pure Python and
runs on Linux, macOS, and Windows. The optional readers are primarily tested on
Linux: Darshan needs `libdarshan-util`, and the `wisio-recorder2parquet`
converter is built with the C++ toolchain. On Windows, WSL is the easiest path
for those formats.
```

## Install from PyPI

For most users the wheel plus the extras for the trace formats you care about
is enough:

```bash
pip install wisio[darshan,dftracer]
```

Add the optional web interface:

```bash
pip install wisio[web]
```

Or install everything:

```bash
pip install wisio[darshan,dftracer,web]
```

The extras are independent:

| Extra | Enables | Notes |
| --- | --- | --- |
| `darshan` | `+analyzer=darshan` | Installs `pydarshan`. **No-op on Python 3.13** because pydarshan does not ship a cp313 wheel. |
| `dftracer` | `+analyzer=dftracer` | Installs `dftracer-utils`. |
| `web` | `streamlit run streamlit_app.py` | Installs Streamlit and Altair. |
| *(none)* | `+analyzer=recorder`, core CLI | Recorder Parquet is read through the core `pyarrow`/Dask stack. |

```{warning}
On Python 3.13, `pip install wisio[darshan]` succeeds but does not install a
working Darshan reader. The marker in `pyproject.toml` makes the extra a no-op
rather than installing a wheel that fails at import. Use Python 3.10–3.12 if
you need Darshan support.
```

Verify the CLI is available:

```bash
wisio --help
```

## Install from source

Source builds also build the optional C++ components (tests and
`wisio-recorder2parquet`) and therefore need a C++20 compiler, Meson, Ninja,
and development packages for Apache Arrow, HDF5, MPI, and Parquet.

```bash
# 1. Install the system dependencies. On Ubuntu 22.04 the list used by CI is
#    the authoritative reference:
#    https://github.com/grc-iit/wisio/blob/main/.github/workflows/ci.yml
#
#    Spack can also provide them:
#    spack -e tools install

# 2. Install the Python build frontend.
python -m pip install --upgrade pip meson-python setuptools wheel

# 3. Install WisIO from the repository root.
pip install .[darshan,dftracer,web] \
  -Csetup-args="--prefix=$HOME/.local" \
  -Csetup-args="-Denable_tests=true" \
  -Csetup-args="-Denable_tools=true"
```

`-Denable_tools=true` builds the `wisio-recorder2parquet` converter described
in {doc}`trace-formats`; `-Denable_tests=true` builds the C++ test
executables. Neither is needed for a Python-only install.

For iterative development, install in editable mode and add the test
requirements:

```bash
pip install -e .[darshan,dftracer]
pip install -r tests/requirements.txt
```

## Dev container and Docker

The repository ships a `.devcontainer.json` and a `Dockerfile` with the
compiler, Arrow, HDF5, and MPI dependencies already installed:

```bash
# Docker
docker build -t wisio .
docker run --rm -it -v "$PWD:/wisio" wisio --help
```

In VS Code, open the repository and choose **Reopen in Container**; the
container installs WisIO with the Darshan and DFTracer extras.

## Working environment on a cluster

WisIO runs on a login node for small traces. For larger traces, use the
`+cluster=` options to submit Dask workers through the scheduler instead of
running everything locally — see {doc}`../user-guide/clusters`.

The Spack environment in `tools/spack.yaml` is the supported way to prepare
the native dependencies on an HPC system:

```bash
spack -e tools install
spack -e tools load
```

## Next steps

- {doc}`quickstart` — run your first analysis on the bundled sample traces.
- {doc}`trace-formats` — which reader to use and what input it expects.
- {doc}`../project/faq` — common installation problems.
