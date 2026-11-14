# FAQ and troubleshooting

## "Either percentile or threshold must be defined"

WisIO needs a way to select significant views. Add one:

```bash
wisio +analyzer=recorder percentile=0.99 trace_path=...
```

`percentile=0.99` keeps the top 1% of views by severity. See
{doc}`../user-guide/analysis` for the difference between percentile and
threshold selection.

## "Cannot instantiate analyzer" / `DarshanAnalyzer` is `Analyzer`

The optional reader is not installed or cannot load. Install the extra for the
format:

```bash
pip install wisio[darshan]    # Python 3.10–3.12
pip install wisio[dftracer]
```

Recorder Parquet needs no extra.

On Python 3.13, the `darshan` extra is deliberately a no-op because pydarshan
does not publish a cp313 wheel. Use Python 3.12 or earlier, or avoid Darshan on
that interpreter. The web app reports the same condition without a traceback.

## Darshan reports fail to load

`pydarshan` needs `libdarshan-util` from the Darshan installation. Loading the
Python module alone is not enough; the shared library must be on the loader
path. On a cluster, load the same Darshan module you used to generate the
reports before running WisIO.

## "No bottlenecks found"

Check, in order:

1. **Selection is too strict.** `percentile=0.999` may leave nothing in a small
   trace. Try `0.99` or `0.95`.
2. **Wrong views.** If you restricted `view_types`, the bottleneck may only be
   visible in another perspective. Try the defaults plus
   `logical_view_types=true`.
3. **Rules were excluded.** Remove `exclude_bottlenecks` /
   `exclude_characteristics` and re-run.
4. **The trace is too small.** A short, uniform trace may genuinely have no
   rule-triggering behavior; check the I/O Characteristics panel for the
   workload size.
5. **Wrong metric.** Try `metrics=[time]` instead of the default `iops`.

```bash
wisio +analyzer=recorder percentile=0.99 \
  output.show_debug=true output.show_characteristics=true \
  trace_path=...
```

The debug tables show how many records survived each stage, which usually
identifies the filter that removed everything.

## `time_granularity` has no effect

Use the analyzer-scoped key:

```bash
wisio ... analyzer.time_granularity=1e7
```

The top-level `time_granularity` in the configuration schema is not passed to
the analyzer. See {doc}`../user-guide/configuration`.

## A SLURM/PBS/LSF run hangs with no workers

The job-queue cluster starts with zero workers unless you request them. The
job-queue config schema does not include `n_workers`, so add it with a plus:

```bash
wisio ... cluster=slurm +cluster.n_workers=8
```

Also verify that compute nodes can reach `cluster.scheduler_options.host`
(defaults to the submitting hostname). See {doc}`../user-guide/clusters`.

## Workers are killed / out of memory

- Raise `cluster.memory_limit` (local cluster) or `cluster.memory` (job queue).
- Reduce `cluster.n_workers`; memory is roughly additive across workers.
- Set `analyzer.view_materialize_max_bytes=0` to keep views on Dask instead of
  materializing them in the client.
- Increase `analyzer.time_granularity` to create fewer time buckets.

## `AttributeError: 'MesonpyOrphan' object has no attribute 'exists'`

This can happen after an editable install (`pip install -e .`) with
meson-python on some platforms: Hydra's plugin discovery trips over the
editable-install loader. Use a non-editable install (`pip install .`) or the
dev container in `CONTRIBUTING.md` until the editable-install path is fixed.

## Where did my results go?

Look for the Hydra run directory printed at the end of the run:

```text
outputs/<date>/<time>/
```

It contains `result.html`, `result.txt`, `result.svg`, `wisio.log`, and the
`bottlenecks/` and `checkpoints/` directories. To pin the location:

```bash
wisio ... hydra.run.dir=/scratch/$USER/wisio-run
```

## The runtime in the report is not my job's wall time

`Runtime` comes from the trace: for record-based formats it is the span from
the earliest start to the latest end timestamp. It is the traced range, which
can differ from the scheduler's wall time (queue time, untraced phases, and
clock skew are not included). Darshan reports carry their own job metadata.

## Can I use WisIO on Windows or macOS?

The core analysis, the CLI, and the DFTracer reader run on Windows, macOS, and
Linux. Darshan requires `libdarshan-util` and is normally used on Linux HPC
systems; Recorder's converter is also Linux-oriented. On Windows, WSL is the
easiest path for those formats.

## What output formats are supported?

The console output is the supported output in this release. It also writes
`result.html`, `result.txt`, and `result.svg` into the run directory. See
{doc}`../user-guide/outputs`.

## Why do the web app and the CLI select different findings?

The web app uses slope-based `threshold` detection (default 45), while the CLI
examples use `percentile`. The underlying views and rules are the same. Pass
the same selection mode if you need identical results.

## What happened to the old grc.iit.edu documentation?

The old Docusaurus pages were retired when the GRC website moved to its v2
structure. This site is now the canonical documentation and is versioned with
the repository.

## How do I cite WisIO?

See {doc}`paper` for the BibTeX entry and the `CITATION.cff` instructions.

## Something else?

Open an issue at <https://github.com/grc-iit/wisio/issues> with:

- the WisIO version (`pip show wisio`),
- Python version and OS,
- the exact command,
- the trace format (and a small reproducer if possible),
- the relevant part of `wisio.log` with `debug=true`.
