<p align="center">
    <img src="https://grc.iit.edu/assets/images/logo-81e1c5c91f2ce84c3ea68ed772a4ef8c.png" width="300">
</p>

# WisIO: Workflow I/O Analysis Tool

![Build and Test](https://github.com/grc-iit/wisio/actions/workflows/ci.yml/badge.svg)
![PyPI - Version](https://img.shields.io/pypi/v/wisio?label=PyPI)
![PyPI - Wheel](https://img.shields.io/pypi/wheel/wisio?label=Wheel)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/wisio?label=Python)

## Overview

WisIO (Wisdom from I/O Behavior) is an open-source tool designed to efficiently analyze multi-terabyte-scale workflow performance data over distributed resources. It provides a comprehensive analysis of I/O performance, identifying bottlenecks and potential root causes through advanced rule-based analysis. With its extensible design, WisIO can be tailored to various use cases, providing actionable insights for improving application performance and resource utilization. By leveraging parallel computing and multi-perspective views, WisIO enables rapid detection of complex I/O issues, making it an invaluable asset for HPC professionals and researchers.

## Installation

To install WisIO through `pip` (recommended for most users):

```bash
# Ensure runtime dependencies for optional features (e.g., Darshan, DFTracer) are installed.
# This might involve using your system's package manager or a tool like Spack.
# Example using Spack to prepare the environment:
# spack -e tools install
pip install wisio[darshan,dftracer]
```

**Note:** On Python 3.13 the `darshan` extra is a no-op (pydarshan does not yet ship a CPython 3.13 wheel). The core WisIO package and `dftracer`/`web` extras work on 3.13+.

To install WisIO from source (for developers or custom builds):

```bash
# 1. Install system dependencies:
#    Refer to the "Install system dependencies" step in .github/workflows/ci.yml
#    (e.g., build-essential, cmake, libarrow-dev, libhdf5-dev, etc.).
#    Alternatively, tools like Spack can help manage these:
#    # spack -e tools install

# 2. Install Python build dependencies:
python -m pip install --upgrade pip meson-python setuptools wheel

# 3. Install WisIO from the root of this repository:
#    The following command includes optional C++ components (tests and tools).
#    The --prefix argument is optional and specifies the installation location.
pip install .[darshan,dftracer] \
  -Csetup-args="--prefix=$HOME/.local" \
  -Csetup-args="-Denable_tests=true" \
  -Csetup-args="-Denable_tools=true"

# (Optional) Install dependencies for running tests if you plan to contribute or run local tests:
# pip install -r tests/requirements.txt
```

## Usage

Here's an example of how to run WisIO with the `recorder` analyzer using sample data included in the repository:

```bash
# Before running, ensure the sample data is extracted.
# For example, to extract the 'recorder-parquet' sample used below:
# mkdir -p tests/data/extracted 
# tar -xzf tests/data/recorder-parquet.tar.gz -C tests/data/extracted
wisio +analyzer=recorder percentile=0.99 trace_path=tests/data/extracted/recorder-parquet
```

This command will analyze the traces and print a summary of I/O characteristics and detected bottlenecks. Below is a sample of the "I/O Characteristics" output:

```
╭───────────────────────────────────── CM1 I/O Characteristics ─────────────────────────────────────╮
│                                                                                                   │
│  Runtime          667.81 seconds                                                                  │
│  I/O Time         4.12 seconds                                                                    │
│                   ├── Read - 0.00 seconds (0.05%)                                                 │
│                   ├── Write - 0.58 seconds (14.08%)                                               │
│                   └── Metadata - 3.53 seconds (85.89%)                                            │
│  I/O Operations   27,463 ops                                                                      │
│                   ├── Read - 1,282 ops (4.67%)                                                    │
│                   ├── Write - 2,303 ops (8.39%)                                                   │
│                   └── Metadata - 23,878 ops (86.95%)                                              │
│  I/O Size         21.18 GiB                                                                       │
│                   ├── Read - 20.03 GiB (94.59%)                                                   │
│                   └── Write - 1.15 GiB (5.41%)                                                    │
│  Read Requests    4 MiB-16 MiB - 1,282 ops                                                        │
│                   └── 4-16 MiB - 1,282 ops (100.00%)                                              │
│  Write Requests   4 kiB-16 MiB - 2,303 ops                                                        │
│                   ├── <4 kiB - 397 ops (17.24%)                                                   │
│                   ├── 4-16 kiB - 1,092 ops (47.42%)                                               │
│                   ├── 16-64 kiB - 722 ops (31.35%)                                                │
│                   ├── 64-256 kiB - 1 ops (0.04%)                                                  │
│                   └── 4-16 MiB - 91 ops (3.95%)                                                   │
│  Nodes            1 node                                                                          │
│  Apps             1 app                                                                           │
│  Processes/Ranks  1,280 processes                                                                 │
│  Files            775 files                                                                       │
│                   ├── Shared: 38 files (4.90%)                                                    │
│                   └── FPP: 737 files (95.10%)                                                     │
│  Time Periods     393 time periods (Time Granularity: 10,000,000.0)                               │
│  Access Pattern   Sequential: 3,585 ops (100.00%) - Random: 0 ops (0.00%)                         │
│                                                                                                   │
╰─ R: Read - W: Write - M: Metadata  ───────────────────────────────────────────────────────────────╯
```

WisIO also identifies potential I/O bottlenecks. Here is a snippet of the "I/O Bottlenecks" section from the same run:

```
╭────────────────── I/O Operations per Second: 25 I/O Bottlenecks with 56 Reasons ──────────────────╮
│                                                                                                   │
│  Time View (4 bottlenecks with 7 reasons)                                                         │
│  ├── [CR1] 32 processes access 2 files within 1 time period (5) across 32 I/O operations and      │
│  │   have an I/O time of 2.19 seconds which is 53.26% of overall I/O time of the workload.        │
│  │   └── [Excessive metadata access] Overall 100.00% (2.19 seconds) of I/O time is spent on       │
│  │       metadata access, specifically 100.00% (2.19 seconds) on the 'open' operation.            │
│  ├── [CR2] 1 process accesses 6 files within 1 time period (634) across 40 I/O operations and     │
│  │   has an I/O time of 0.33 seconds which is 7.97% of overall I/O time of the workload.          │
│  │   ├── [Excessive metadata access] Overall 99.35% (0.33 seconds) of I/O time is spent on        │
│  │   │   metadata access, specifically 99.13% (0.33 seconds) on the 'open' operation.             │
# ... (further bottleneck details omitted for brevity) ...
│                                                                                                   │
╰───────────────────────────────────────────────────────────────────────────────────────────────────╯
```

**Output artifacts:** The console output also saves `result.html`, `result.txt`, and `result.svg` in the Hydra run directory for sharing and archiving.

## WisIO Web App

WisIO includes a browser-based interface ("WisIO Web") for interactive analysis:

```bash
# Install the web extra (Streamlit + Altair)
pip install wisio[web]

# Launch the app
streamlit run streamlit_app.py
```

Features:
- **Drag-and-drop trace upload** (max 20 MB per upload, auto-detects Darshan/DFTracer/Recorder format)
- **Interactive bottleneck exploration** with severity-badged findings (Critical → Trivial)
- **Altair visualizations** of I/O characteristics and operation distributions
- **Runs on Streamlit Community Cloud** — try the live instance at <https://wisio-web.streamlit.app/> or deploy your own from the repo

The web app uses the same analysis engine and rule set as the CLI, so results are consistent.

## Further Information

For more details, to report issues, or to contribute to WisIO, please refer to the following resources:

*   **[Official WisIO Documentation](https://grc.iit.edu/docs/category/wisio/)**: For detailed usage, configuration options, and information about analyzers.
*   **[Issue Tracker](https://github.com/grc-iit/wisio/issues)**: To report bugs or suggest new features.
*   **[Contributing Guidelines](./CONTRIBUTING.md)**: For information on how to contribute to the project, including setting up a development environment and coding standards.
*   **[Citation File](./CITATION.cff)**: If you use WisIO in your research, please cite it using the information in this file.

## Acknowledgments

This work was performed under the auspices of the U.S. Department of Energy by Lawrence Livermore National Laboratory under Contract DE-AC52-07NA27344. This material is based upon work supported by the U.S. Department of Energy, Office of Science, Office of Advanced Scientific Computing Research under the DOE Early Career Research Program (LLNL-CONF-862440). Also, this research is supported in
part by the National Science Foundation (NSF) under Grants OAC-2104013, OAC-2313154, and OAC-2411318.
