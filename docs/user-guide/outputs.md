# Output and artifacts

WisIO's default output is a pair of console panels plus three saved artifacts
in the Hydra run directory.

## The I/O Characteristics panel

This panel summarizes the whole workload:

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
│  I/O Size         21.18 GiB                                                                       │
│                   ├── Read - 20.03 GiB (94.59%)                                                   │
│                   └── Write - 1.15 GiB (5.41%)                                                    │
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

The panel title is prefixed with `output.name` when it is set. Hide the panel
with `output.show_characteristics=false`.

The meaning of each row is documented in {doc}`bottlenecks`; the
`Time Granularity` value is the `analyzer.time_granularity` used for the run.

## The I/O Bottlenecks panel

This panel groups findings by perspective (view name), then by severity:

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

- The title names the metric (`I/O Operations per Second` for `iops`) and the
  total bottleneck/reason counts.
- Each section is a view name (`Time View`, `File View`, `Process View`, …).
- `[CR1]` is severity + finding index. See {doc}`analysis` for the severity
  codes and {doc}`bottlenecks` for the reasons.

### Output controls

| Override | Effect |
| --- | --- |
| `output.name=label` | Prefix panels with a custom label. |
| `output.max_bottlenecks=10` | Show more findings per view (default 3). |
| `output.compact=true` | Shorter subjects and descriptions. |
| `output.group_behavior=true` | Group findings with similar I/O behavior. |
| `output.root_only=false` | Also show nested perspectives (depth > 1). |
| `output.view_names=[file_name,proc_name]` | Show only these view names; overrides `root_only`. |
| `output.show_header=false` | Hide panel titles. |
| `output.show_characteristics=false` | Hide the first panel. |
| `output.show_debug=true` | Add retention, severity, throughput, and timing tables. |

## Artifacts

Every run writes to its Hydra run directory:

```text
outputs/2025-06-08/14-32-07/
├── wisio.log
├── result.html
├── result.txt
├── result.svg
├── bottlenecks/
│   ├── _metadata
│   ├── part.0.parquet
│   └── ...
└── checkpoints/
    ├── ...
```

| Artifact | Contents |
| --- | --- |
| `result.txt` | Plain-text rendering of the console report. |
| `result.html` | Self-contained HTML version, suitable for sharing or attaching to a report. |
| `result.svg` | Vector rendering of the console panels. |
| `wisio.log` | Run log (INFO by default; `debug=true` adds detail). |
| `bottlenecks/` | Per-view bottleneck records as Parquet, used to render output. |
| `checkpoints/` | Cached intermediate views/metrics so a re-run can skip recomputation. |

To keep artifacts in a known place:

```bash
wisio +analyzer=recorder percentile=0.99 \
  hydra.run.dir=/scratch/$USER/wisio-run \
  trace_path=/path/to/parquet-traces
```

## Checkpoints

With `analyzer.checkpoint=true` (the default), WisIO caches the main view,
view results, and metric boundaries under
`analyzer.checkpoint_dir`. Re-running the same command with the same
checkpoint directory reuses them, which is useful while iterating on rules or
output options.

```bash
# Disable checkpoints for a clean run
wisio +analyzer=recorder percentile=0.99 analyzer.checkpoint=false ...

# Keep checkpoints in a stable location across runs
wisio +analyzer=recorder percentile=0.99 \
  analyzer.checkpoint_dir=/scratch/$USER/wisio-checkpoints ...
```

```{note}
Checkpoint names include the view types and metrics that produced them, but
**not** `analyzer.time_granularity`. If you change the granularity while
reusing a stable `analyzer.checkpoint_dir`, use a fresh checkpoint directory
or disable checkpointing for that run; otherwise the cached main view is
reused and the new granularity has no effect.
```

## Debug output

`output.show_debug=true` adds tables for:

- **Retention** — how many records survived each stage (raw → main view →
  perspective → critical view).
- **Severities** — counts per severity and metric.
- **Counts** — perspectives, bottlenecks, and rules processed.
- **Throughputs** — records and rules per second.

This is mainly useful when tuning performance or investigating why a finding
was or was not selected.
