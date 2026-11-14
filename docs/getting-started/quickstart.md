# Quick start

This walkthrough uses the small Recorder Parquet trace that ships with the
repository, so it needs no cluster and no optional reader.

## 1. Install WisIO

```bash
pip install wisio
```

Recorder Parquet needs no extra. If you plan to analyze Darshan or DFTracer
traces, install the corresponding extra as described in
{doc}`installation`.

## 2. Extract a sample trace

The test data is stored as compressed archives. Extract the Recorder sample:

```bash
mkdir -p tests/data/extracted/recorder-parquet
tar -xzf tests/data/recorder-parquet.tar.gz \
  -C tests/data/extracted/recorder-parquet
```

The directory now contains `global.json` and one or more `part.*.parquet`
files. That directory — not an individual Parquet file — is the `trace_path`.

## 3. Run the analysis

```bash
wisio +analyzer=recorder percentile=0.99 \
  trace_path=tests/data/extracted/recorder-parquet
```

```{important}
`percentile` or `threshold` must be provided. With the default configuration
both are `None`, and WisIO exits with
`ValueError: Either percentile or threshold must be defined`.
`percentile=0.99` means "consider the top 1% of views by severity score".
```

WisIO prints two panels. The first summarizes the workload:

```text
╭───────────────────────────────────── CM1 I/O Characteristics ─────────────────────────────────────╮
│  Runtime          667.81 seconds                                                                  │
│  I/O Time         4.12 seconds                                                                    │
│                   ├── Read - 0.00 seconds (0.05%)                                                 │
│                   ├── Write - 0.58 seconds (14.08%)                                               │
│                   └── Metadata - 3.53 seconds (85.89%)                                            │
│  I/O Operations   27,463 ops                                                                      │
│                   ├── Read - 1,282 ops (4.67%)                                                    │
│                   ├── Write - 2,303 ops (8.39%)                                                   │
│                   └── Metadata - 23,878 ops (86.95%)                                              │
│  ...                                                                                              │
╰─ R: Read - W: Write - M: Metadata  ───────────────────────────────────────────────────────────────╯
```

The second panel lists detected bottlenecks, grouped by perspective, with
severity codes such as `[CR1]` (critical) and human-readable reasons:

```text
╭────────────────── I/O Operations per Second: 25 I/O Bottlenecks with 56 Reasons ──────────────────╮
│  Time View (4 bottlenecks with 7 reasons)                                                         │
│  ├── [CR1] 32 processes access 2 files within 1 time period (5) across 32 I/O operations and      │
│  │   have an I/O time of 2.19 seconds which is 53.26% of overall I/O time of the workload.        │
│  │   └── [Excessive metadata access] Overall 100.00% (2.19 seconds) of I/O time is spent on       │
│  │       metadata access, specifically 100.00% (2.19 seconds) on the 'open' operation.            │
│  ...                                                                                              │
╰───────────────────────────────────────────────────────────────────────────────────────────────────╯
```

With `percentile=0.99`, every selected row falls in the top severity bin, so
the codes in this example are all `CR`. Lower the percentile (for example
`0.5`) to see `high`, `medium`, and other severities. See
{doc}`../user-guide/analysis` for how severities are computed and
{doc}`../user-guide/bottlenecks` for the rule catalogue.

## 4. Find the artifacts

Every run gets a Hydra output directory. The console output is also saved
there:

```text
outputs/2025-06-08/14-32-07/
├── wisio.log
├── result.html
├── result.txt
├── result.svg
├── bottlenecks/
└── checkpoints/
```

`result.html` is the shareable version of the console report. The
`bottlenecks/` directory holds the Parquet records used by the output layer;
`checkpoints/` lets a re-run skip the expensive stages. See
{doc}`../user-guide/outputs`.

## Common variations

Analyze the same trace with the `time` metric instead of `iops`:

```bash
wisio +analyzer=recorder percentile=0.99 metrics=[time] \
  trace_path=tests/data/extracted/recorder-parquet
```

Restrict the analysis to file and process views:

```bash
wisio +analyzer=recorder percentile=0.99 \
  view_types=[file_name,proc_name] \
  trace_path=tests/data/extracted/recorder-parquet
```

Add logical views such as app, node, rank, directory, and file pattern:

```bash
wisio +analyzer=recorder percentile=0.99 logical_view_types=true \
  trace_path=tests/data/extracted/recorder-parquet
```

Use a different time bucket (the parameter lives under `analyzer`, not at the
top level):

```bash
wisio +analyzer=recorder percentile=0.99 analyzer.time_granularity=1e8 \
  trace_path=tests/data/extracted/recorder-parquet
```

## Next steps

- {doc}`trace-formats` — Darshan, DFTracer, and Recorder inputs.
- {doc}`../user-guide/cli` — the full command-line interface.
- {doc}`../user-guide/configuration` — every parameter.
- {doc}`../user-guide/interactive-analysis` — explore the same trace in a Jupyter notebook.
- {doc}`../user-guide/web-app` — the browser interface.
