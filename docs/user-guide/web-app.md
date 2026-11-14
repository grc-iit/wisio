# WisIO Web

WisIO includes a browser interface built with Streamlit. It runs the same
analysis engine and rule set as the CLI.

- **Hosted instance:** <https://wisio-web.streamlit.app/>
- **Local app:** `streamlit_app.py` in the repository root

For scripted exploration, inspecting intermediate views, or batch runs, use the
Jupyter workflow in {doc}`interactive-analysis` instead.

## Running locally

```bash
pip install wisio[web]
streamlit run streamlit_app.py
```

The `web` extra installs Streamlit and Altair. The app also needs the reader
for whichever trace type you upload:

```bash
# Recorder Parquet works with the core install.
pip install wisio[web]

# Add Darshan and/or DFTracer if you upload those formats.
pip install wisio[web,darshan,dftracer]
```

## What the app supports

| Input | Detection |
| --- | --- |
| Darshan reports (`.darshan`) | Analyzer `darshan` |
| Recorder Parquet (`.parquet`) | Analyzer `recorder` |
| DFTracer (`.pfw`, `.pfw.gz`) | Analyzer `dftracer` |

- Upload **all files from one run at once**; mixing formats in one upload is
  rejected.
- The total upload is limited to **20 MB per analysis** because the hosted
  instance runs on Streamlit Community Cloud (2.7 GB / 2 cores). Larger runs
  should use the CLI on your own machine.
- The app detects the analyzer from the file extensions and reports a clear
  error if the matching reader is not installed (notably Darshan on Python
  3.13).

## Options

| Control | Maps to | Notes |
| --- | --- | --- |
| **Perspectives** | `view_types` | File, Process, Timeline; Timeline disables the granularity slider when unselected. |
| **Time granularity** | `analyzer.time_granularity` | Slider labeled seconds (1–100, default 5); the app passes `value × 1e6` to the analyzer, which matches DFTracer's microsecond timestamps. |
| **Threshold** | `threshold` | 0–90, default 45; slope-based detection (see {doc}`analysis`). |
| **Logical view types** | `logical_view_types` | App, node, rank, directory, and file-pattern views; slower. |

The app always runs a single local Dask worker with a 2.2 GB memory limit and
checkpointing disabled, so each upload is independent.

## Results

Results are shown in two tabs:

- **I/O Characteristics** — the same summary as the CLI panel, with Altair
  charts for operation and size distributions.
- **I/O Bottlenecks** — expandable findings with a colored severity badge,
  subject, I/O time share, operation share, and reasons. Up to 20 findings per
  view are rendered; the rest are summarized as *"N more not shown, worst
  first."*

Uploaded files are written to a temporary directory, analyzed, and deleted.
Results remain in the browser session until it is reloaded or closed.

## Deploying your own instance

The hosted app is deployed from this repository with
[`requirements.txt`](https://github.com/grc-iit/wisio/blob/main/requirements.txt),
which installs `.[darshan,dftracer,web]`. On Streamlit Community Cloud:

1. Create an app from the `grc-iit/wisio` repository, branch `main`, main file
   `streamlit_app.py`.
2. In **Advanced settings**, pin **Python 3.12**. Darshan requires a pydarshan
   wheel, which is not available for 3.13.
3. Deploy. No other configuration is required.

For private deployments or larger uploads, run the app on a machine with more
memory and, if needed, raise `MAX_TOTAL_UPLOAD_MB` in `streamlit_app.py` (the
server's per-file limit also needs to be raised via Streamlit config).

## Limitations

- One analysis at a time; no batch uploads.
- No cluster configuration; the app always uses a single local worker.
- No checkpoint reuse between uploads.
- The web app uses slope-based `threshold` detection, while the CLI examples
  use `percentile`. Both run the same rules, so findings are comparable, but
  the selection mechanism differs.
