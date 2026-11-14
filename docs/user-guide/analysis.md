# How analysis works

WisIO turns raw I/O trace records into ranked, explained findings in a Dask
pipeline. This page describes the concepts a user needs to read the output;
the implementation is covered in {doc}`../development/architecture`.

```{mermaid}
flowchart LR
    A[Read trace] --> B[Post-process]
    B --> C[High-level metrics]
    C --> D[Main view]
    D --> E[Perspectives]
    E --> F[Score]
    F --> G[Apply rules]
    G --> H[Console output]
    classDef step fill:#ffffff,stroke:#d31f30,stroke-width:1.6px,color:#333333
    class A,B,C,D,E,F,G,H step
```

## Views and perspectives

A **view** aggregates trace records by one or more dimensions:

| View type | Groups by | Example |
| --- | --- | --- |
| `time_range` | Time bucket | All operations in bucket 42 |
| `file_name` | File path | `/scratch/out/field_0007.bin` |
| `proc_name` | Composite process ID (`app#host#rank_or_pid#thread`) | `app#node042#17#0` |
| `app_name` | Application name | `app` (logical) |
| `node_name` | Hostname | `node042` (logical) |
| `rank` | MPI rank | `17` (logical) |
| `file_dir` | File directory | `/scratch/out` (logical) |
| `file_pattern` | File name with digits replaced | `/scratch/out/field_[0-9].bin` (logical) |

The three primary types are enabled by `view_types`; the logical types are
enabled with `logical_view_types=true`.

A **perspective** is an ordered combination of view types. With the default
three types, WisIO evaluates every ordered non-empty permutation:

```text
(time_range) (file_name) (proc_name)
(time_range, file_name) (file_name, time_range)
(time_range, proc_name) (proc_name, time_range)
(file_name, proc_name) (proc_name, file_name)
(time_range, file_name, proc_name)  ... and the other 5 orderings
```

That is 15 perspectives per metric. Order matters because the first view type
is the grouping key and the rest describe the subjects inside each group. For
example, `(time_range, proc_name, file_name)` asks *"which processes touching
which files are slow within each time bucket?"*.

Logical views add up to five more perspectives per metric:
`proc_name → app_name`, `proc_name → node_name`, `proc_name → rank`,
`file_name → file_dir`, and `file_name → file_pattern`. They are only
computed when their parent view type is enabled.

Because the search space grows quickly, `view_types` and
`logical_view_types` are the main knobs for trading coverage against runtime.

## Metrics and scoring

Each view row is scored on the selected metric. Two metrics are implemented:

### `iops` (default)

`iops` ranks rows by *efficiency*, not by absolute operation count:

```text
slope = (row ops / total ops) / (row I/O time / total I/O time)
```

- `slope < 1` means the row consumes a larger share of I/O time than its share
  of operations — the signature of a bottleneck.
- `slope > 1` means it is doing more work per second than average.
- The percentile rank is computed on `1 / slope`, so the slowest rows rank
  highest.

This is why a view with a tiny fraction of the operations can still be
reported as critical: it is taking far more than its share of the time.

### `time`

`time` ranks rows by I/O time relative to a boundary (the slowest process, or
the total time when there is no process view):

```text
slope = row I/O time / boundary
```

Higher is worse. Use `metrics=[time]` when you care about absolute I/O time
rather than efficiency.

### Severities

Scores are binned into eight severities. Console output abbreviates them:

| Severity | Code | Meaning |
| --- | --- | --- |
| `critical` | `CR` | Worst bin; act first |
| `very high` | `VH` | |
| `high` | `HI` | |
| `medium` | `MD` | |
| `low` | `LO` | |
| `very low` | `VL` | |
| `trivial` | `TR` | |
| `none` | `NA` | Not a bottleneck under the current selection |

The bin cut points for percentile scoring are `0, 0.001, 0.01, 0.1, 0.25,
0.5, 0.75, 0.9`. Because selection and scoring use the same percentile scale,
`percentile=0.99` keeps rows at or above 0.99 — all of which land in the top
bin, so a `0.99` run displays `[CR…]` findings. Lower the percentile (for
example `0.25`) to see `medium`, `high`, and `very high` findings as well. In
threshold mode the selected slope range spans several bins, so severities are
mixed.

## Selecting findings: percentile vs threshold

### `percentile` (recommended)

`percentile=0.99` keeps views whose severity rank is at or above the 99th
percentile. It works for both `iops` and `time` and is what the examples and
CI use.

```bash
wisio +analyzer=recorder percentile=0.99 trace_path=...
```

### `threshold` (slope-based)

`threshold` keeps rows whose slope is at or below a cutoff instead of using a
percentile:

- for `iops`, the value is an **angle in degrees** (0–90) and the cutoff is
  `tan(degrees)`;
- for `time`, the value is a fraction.

```bash
wisio +analyzer=dftracer threshold=45 trace_path=...
```

The threshold path is newer and less exercised than percentile mode. Use it
when you specifically want slope-based sensitivity; otherwise use
`percentile`.

## Time granularity

`analyzer.time_granularity` controls how many `time_range` buckets the trace
is split into. Smaller values produce more, narrower buckets and therefore
more time perspectives; larger values produce fewer buckets and a faster
analysis.

The unit follows the analyzer's native timestamps:

| Analyzer | Default | Effective bucket |
| --- | --- | --- |
| `dftracer` | `1e6` | 1 s (microsecond timestamps) |
| `darshan` | `1e3` | 1 ms (start times in seconds) |
| `recorder` | `1e7` | 10 ms (nanosecond `tmid`) |

## Excluding work

Two lists narrow the rule stage without changing the views or the scoring:

- `exclude_bottlenecks` — rule keys from {doc}`bottlenecks`, e.g.
  `small_writes`.
- `exclude_characteristics` — characteristic keys, e.g. `io_size`.

```bash
wisio +analyzer=recorder percentile=0.99 \
  exclude_bottlenecks=[small_reads,small_writes] \
  exclude_characteristics=[read_xfer_size,write_xfer_size] \
  trace_path=...
```

## What the analysis does not do

- Only `iops` and `time` are computed. `bw`, `intensity`, and `att_perf`
  appear in the `Metric` type but are not wired into the current scoring path.
- `accuracy` is not a runtime parameter; traces are analyzed as recorded.
- The analysis is read-only with respect to the trace; checkpoints and
  results go to the output directory.
