# WisIO Documentation

```{image} _static/img/wisio-logo.png
:alt: WisIO
:width: 220px
:align: center
:class: wisio-hero-logo
```

<p align="center">
  <a href="https://pypi.org/project/wisio/"><img src="https://img.shields.io/pypi/v/wisio?label=PyPI" alt="PyPI"></a>
  <a href="https://pypi.org/project/wisio/"><img src="https://img.shields.io/pypi/pyversions/wisio?label=Python" alt="Python versions"></a>
  <a href="https://doi.org/10.1145/3721145.3725742"><img src="https://img.shields.io/badge/DOI-10.1145%2F3721145.3725742-blue" alt="DOI"></a>
  <a href="https://github.com/grc-iit/wisio"><img src="https://img.shields.io/badge/source-grc--iit%2Fwisio-181717?logo=github" alt="Source"></a>
</p>

**WisIO** (*Wisdom from I/O Behavior*) analyzes multi-terabyte-scale HPC
workflow I/O traces, detects performance bottlenecks from multiple
perspectives, and explains their likely root causes using an extensible rule
engine.

It is designed for application developers, HPC users, and system
administrators who need to answer questions like *"why is my simulation
spending so much time in I/O?"* without manually sifting through millions of
trace records.

::::{grid} 1 2 2 3
:gutter: 3

:::{grid-item-card} Install and run
:link: getting-started/installation
:link-type: doc

Install from PyPI, point WisIO at a trace, and get a diagnosis in one command.
:::

:::{grid-item-card} Interactive analysis
:link: user-guide/interactive-analysis
:link-type: doc

Inspect views, plot distributions, and run batch experiments in Jupyter
notebooks.
:::

:::{grid-item-card} WisIO Web
:link: user-guide/web-app
:link-type: doc

Upload a trace and explore severity-badged findings in the browser.
:::

:::{grid-item-card} Understand the output
:link: user-guide/analysis
:link-type: doc

Learn what the I/O characteristics, perspectives, severities, and bottleneck
descriptions mean.
:::

:::{grid-item-card} Configure it
:link: user-guide/configuration
:link-type: doc

Every Hydra parameter: analyzers, views, metrics, clusters, and console output.
:::

::::

## Quick start

```bash
pip install wisio   # add [darshan] or [dftracer] for those formats, [web] for the app
wisio +analyzer=recorder percentile=0.99 trace_path=path/to/parquet-traces
```

WisIO writes `result.html`, `result.txt`, and `result.svg` into the Hydra run
directory under `outputs/`. See {doc}`getting-started/quickstart` for a
walkthrough using the sample traces included in the repository.

## Interactive analysis

For exploratory work, the `notebooks/` directory contains Jupyter workflows
that drive the same analyzer API as the CLI. Keep the intermediate views in the
kernel, inspect one perspective, plot distributions, or run the notebook over a
list of traces with Papermill.

```bash
pip install -r notebooks/requirements.txt
jupyter lab notebooks/analysis.ipynb
```

See {doc}`user-guide/interactive-analysis` for the maintained notebook,
parameters, and batch runs.

Prefer a browser? {doc}`user-guide/web-app` offers drag-and-drop uploads and
interactive findings with no local setup.

## Why WisIO

- **Multi-perspective analysis.** The same trace is examined by time period,
  file, and process — and by logical combinations such as app, node, rank,
  directory, and file pattern — so a bottleneck that only appears when one
  process touches one file during one time window is still found.
- **Rule-based root causes.** Findings are not just ranked; WisIO attaches
  human-readable reasons such as *"99% of I/O time is spent in metadata
  access, specifically on `open`."*
- **Built for scale.** Analysis runs on Dask, so traces can be processed
  across cores, nodes, or a job scheduler (LSF, PBS, SLURM) without loading
  everything into memory.
- **Extensible.** Trace readers, bottleneck rules, characteristics, and
  outputs are separate components. New formats or domain-specific rules can
  be added without reworking the pipeline.

```{toctree}
:hidden:
:caption: Getting started
:maxdepth: 1

getting-started/installation
getting-started/quickstart
getting-started/trace-formats
```

```{toctree}
:hidden:
:caption: User guide
:maxdepth: 1

user-guide/cli
user-guide/configuration
user-guide/analysis
user-guide/bottlenecks
user-guide/outputs
user-guide/clusters
user-guide/interactive-analysis
user-guide/web-app
```

```{toctree}
:hidden:
:caption: Development
:maxdepth: 1

development/architecture
development/python-api
development/contributing
```

```{toctree}
:hidden:
:caption: Project
:maxdepth: 1

project/paper
project/faq
project/changelog
```

## Citing WisIO

If WisIO contributes to a publication, please cite both the software and the
ICS'25 paper:

```bibtex
@inproceedings{yildirim2025wisio,
  author    = {Yildirim, Izzet and Devarajan, Hariharan and Kougkas, Anthony
               and Sun, Xian-He and Mohror, Kathryn},
  title     = {{WisIO}: Automated {I/O} Bottleneck Detection with
               Multi-Perspective Views for {HPC} Workflows},
  booktitle = {Proceedings of the 2025 ACM International Conference on
               Supercomputing (ICS'25)},
  year      = {2025},
  doi       = {10.1145/3721145.3725742}
}
```

See {doc}`project/paper` for the full citation and `CITATION.cff` in the
repository root.
