# Trace formats

WisIO does not define a new trace format. It reads traces produced by existing
I/O tracing tools through an *analyzer* selected with `+analyzer=<name>`.

| Analyzer | Input | Optional extra | Main views | Default `analyzer.time_granularity` |
| --- | --- | --- | --- | --- |
| `darshan` | A `.darshan` file or a directory of them | `darshan` | `time_range`, `file_name`, `proc_name` (DXT); `file_name`, `proc_name` only (non-DXT) | `1e3` |
| `dftracer` | A directory of `.pfw` / `.pfw.gz` files | `dftracer` | all | `1e6` |
| `recorder` | A directory of Parquet files plus `global.json` | none | all | `1e7` |

The main view types are explained in {doc}`../user-guide/analysis`.

## Darshan

```bash
pip install wisio[darshan]
wisio +analyzer=darshan percentile=0.99 trace_path=/path/to/darshan-reports
```

`trace_path` may be either a single `*.darshan` file or a directory; a
directory is globbed for `*.darshan` files and all reports are combined into
one analysis. `pydarshan` must be able to load the reports, so the
`libdarshan-util` shared library must be available (normally installed with
Darshan itself).

Darshan reports come in two shapes:

- **DXT (`DXT_POSIX` records).** Per-operation records with timestamps,
  hostnames, offsets, and sizes. This is the richest mode: all three main
  views, all logical views, and time-period analysis are available.
- **Non-DXT (aggregated counters).** Only per-file and per-process totals are
  available. WisIO supports only the `file_name` and `proc_name` view types
  here; asking for `time_range` raises a `ValueError`. Use:

  ```bash
  wisio +analyzer=darshan percentile=0.99 \
    view_types=[file_name,proc_name] \
    trace_path=/path/to/darshan-reports
  ```

Darshan DXT start times are in seconds, and the default
`analyzer.time_granularity=1e3` therefore produces millisecond-sized time
buckets. Override it under `analyzer`, not at the top level:

```bash
wisio +analyzer=darshan percentile=0.99 analyzer.time_granularity=1e2 ...
```

```{important}
Darshan support on Python 3.13 is intentionally disabled because pydarshan
does not ship a cp313 wheel. Use Python 3.10–3.12 for Darshan analyses.
```

## DFTracer

```bash
pip install wisio[dftracer]
wisio +analyzer=dftracer percentile=0.99 trace_path=/path/to/pfw-traces
```

`trace_path` is a directory containing `.pfw` or `.pfw.gz` files. WisIO reads
both POSIX and DLIO events. DFTracer timestamps are in microseconds; the
default `analyzer.time_granularity=1e6` gives one-second time buckets.

```bash
# Finer buckets (100 ms) for short traces
wisio +analyzer=dftracer percentile=0.99 analyzer.time_granularity=1e5 ...

# Coarser buckets (10 s) for very long traces
wisio +analyzer=dftracer percentile=0.99 analyzer.time_granularity=1e7 ...
```

## Recorder

Recorder writes raw text traces; WisIO analyzes the Parquet form. The expected
input directory contains one or more `part.*.parquet` files and a
`global.json` file with the global `tmid` range:

```text
{"file_id": [...], "proc_id": [...], "tmid": [0, 6683055996]}
```

```bash
wisio +analyzer=recorder percentile=0.99 trace_path=/path/to/parquet-traces
```

Recorder timestamps are nanoseconds in `tmid` (while `tstart`/`tend` are in
seconds), so the default `analyzer.time_granularity=1e7` produces 10 ms
buckets.

### Converting raw Recorder traces

The repository includes a C++ converter, `wisio-recorder2parquet`, built only
when `-Denable_tools=true` is passed to the source install:

```bash
wisio-recorder2parquet /path/to/raw-recorder-trace
```

It writes Parquet files into a `_parquet` subdirectory of the input directory;
point `trace_path` at that subdirectory. On a parallel file system the
conversion can be run under MPI:

```bash
mpirun -n 8 wisio-recorder2parquet /path/to/raw-recorder-trace
```

The bundled `tests/data/recorder-raw.tar.gz` and
`tests/data/recorder-parquet.tar.gz` archives show the expected raw and
converted layouts.

### Recorder Parquet columns

| Column | Type | Meaning |
| --- | --- | --- |
| `tstart`, `tend` | float (seconds) | Start and end of the operation |
| `tmid` | int64 (nanoseconds) | Midpoint timestamp used for time bucketing |
| `duration` | float (seconds) | Operation duration |
| `hostname` | string | Host where the operation ran |
| `app` | string | Application name |
| `rank` | int | MPI rank |
| `proc_name` | string | `app#host#rank#thread` composite process identifier |
| `proc_id` | int64 | Recorder process identifier |
| `thread_id` | int | Thread identifier |
| `cat` | int | Trace category (POSIX records are analyzed) |
| `io_cat` | int | 1 = read, 2 = write, 3 = metadata |
| `func_id` | string | I/O function, e.g. `open`, `read`, `write` |
| `acc_pat` | int | 0 = sequential, 1 = random |
| `file_id` | int64 | Recorder file identifier |
| `file_name` | string | File path |
| `size` | int64 (bytes) | Transfer size |
| `bandwidth` | float | Transfer bandwidth recorded by Recorder |

## Choosing an analyzer

- Use **Darshan** for production HPC jobs that already run with Darshan
  enabled, especially when DXT is available.
- Use **DFTracer** for AI/ML workloads and applications instrumented with
  DFTracer (POSIX or DLIO).
- Use **Recorder** when you need fine-grained, low-overhead tracing and
  already have raw Recorder output; convert it to Parquet first.

All three readers feed the same analysis pipeline, so views, rules, and
outputs behave consistently across formats.
