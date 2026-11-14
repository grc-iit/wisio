# Architecture

WisIO separates trace reading, analysis, rule evaluation, and presentation so
that a new trace format or a new diagnostic rule does not require changing the
others.

## System overview

```{image} ../_static/img/architecture.svg
:alt: WisIO architecture: I/O traces from Darshan, DFTracer, and Recorder are read into a normalized record schema, aggregated into a main view, expanded into perspectives, scored, and evaluated by bottleneck and characteristic rules to produce a console report and the interactive analysis.
:width: 100%
```

Readers normalize each format into the same record schema, so everything from
aggregation onward is format-independent. The rest of this page describes each
stage and its extension points.

## Repository layout

```text
wisio/
├── __main__.py          # `wisio` entry point: Hydra config → cluster → analyzer → output
├── config.py            # Dataclass configuration and Hydra ConfigStore groups
├── analyzer.py          # Analyzer base class: read → aggregate → views → score → rules
├── analysis.py          # Metric formulas, bins, severity names
├── scoring.py           # ViewEvaluator: turns view rows into scored rows
├── rules.py             # Known rules, characteristics, and their handlers
├── rule_engine.py       # Runs characteristics and bottleneck rules in parallel
├── output.py            # ConsoleOutput and artifact rendering
├── constants.py         # Column names, view types, transfer-size bins, labels
├── types.py             # Dataclasses and enums shared across the package
├── darshan.py           # Darshan reader/analyzer (DXT and non-DXT)
├── dftracer.py          # DFTracer .pfw reader/analyzer
├── recorder.py          # Recorder Parquet reader/analyzer
└── utils/               # Dask helpers, JSON encoders, logging
streamlit_app.py         # WisIO Web
bottleneck_report.py     # Web: turns bottleneck records into display objects
uploads.py               # Web: upload filename sanitization
tools/recorder2parquet.cpp
subprojects/             # Meson wraps: recorder, cpp-logger, backward-cpp
```

## Pipeline

```{mermaid}
flowchart LR
    A[Read] --> B[Aggregate] --> C[Perspectives] --> D[Score] --> E[Rules] --> F[Report]
    classDef step fill:#ffffff,stroke:#d31f30,stroke-width:1.6px,color:#333333
    class A,B,C,D,E,F step
```

### 1. Read and post-process

Each analyzer implements `read_trace()` to produce a Dask DataFrame with a
common schema:

| Column | Meaning |
| --- | --- |
| `time` | Operation duration |
| `count` | Number of operations represented by the row |
| `size` | Bytes transferred |
| `io_cat` | 1 = read, 2 = write, 3 = metadata |
| `acc_pat` | 0 = sequential, 1 = random |
| `func_id` | I/O function name |
| `file_name` | File path |
| `proc_name` | `app#host#rank_or_pid#thread` composite identifier (rank for Darshan/Recorder, PID for DFTracer) |

`read_stats()` computes the job runtime and raw record count; `postread_trace()`
applies format-specific normalization. Derived columns (file directory, file
pattern, app/node/rank parts, metadata operations) are added on demand by the
view and rule stages.

### 2. Aggregate

`compute_high_level_metrics()` aggregates the trace into a main view keyed by
the selected `view_types`. This is the expensive pass over the trace: after it,
all perspectives are small enough to compute from the main view rather than
from raw records.

The main view is repartitioned to roughly 256 MiB partitions. If a main view is
small enough (`analyzer.view_materialize_max_bytes`, default 64 MiB), the
remaining view loop runs in pandas for speed; otherwise everything stays on
Dask. Setting the parameter to `0` forces the Dask path.

### 3. Perspectives

`compute_views()` evaluates every ordered permutation of `view_types` (see
{doc}`../user-guide/analysis`). `compute_logical_views()` adds app, node, rank,
directory, and file-pattern views when `logical_view_types=true`. Each
perspective is grouped by its first view type, with the remaining types kept
as subject columns.

### 4. Score

`ViewEvaluator` computes the metric slope for each row (`analysis.set_metric_slope`)
and bins it into a severity (`analysis.set_metric_scores`). A critical view is
selected from the score distribution using either the percentile or the
slope threshold.

### 5. Apply rules

`RuleEngine.process_characteristics()` computes workload-level statistics;
`process_bottlenecks()` evaluates the six bottleneck rules against every
perspective's scored rows and attaches reasons. Both stages run as Dask task
graphs. Findings are written to `analyzer.bottleneck_dir` as Parquet.

### 6. Present

`ConsoleOutput` reads the bottleneck Parquet files, renders the
characteristics and bottleneck panels with Rich, prints them, and saves
`result.html`, `result.txt`, and `result.svg`. See {doc}`../user-guide/outputs`.

## Checkpointing

When `analyzer.checkpoint=true`, intermediate results are stored as:

- Parquet directories for the main view and each perspective, written with a
  `_metadata` file so they can be read back cheaply;
- JSON for scalar data such as metric boundaries and raw statistics.

Checkpoint names include the sorted view types and metrics that produced them,
so changing an analysis parameter produces a different key rather than reading
an incompatible checkpoint.

## Concurrency model

- The trace and main view are Dask collections; grouping, aggregation, and
  scoring are expressed as Dask operations.
- Rules and characteristics are built as delayed tasks and resolved in a single
  `compute`, so independent rules share one scheduler pass.
- The output layer is client-side: it computes bottleneck records and renders
  them in the submitting process.

## Extension points

### A new trace format

1. Subclass `wisio.analyzer.Analyzer` and implement `read_trace()` (and
   `postread_trace()` / `read_stats()` if the format needs it).
2. Emit the common columns listed above.
3. Register a dataclass in `wisio/config.py` with `_target_` pointing at the
   class, and `cs.store(group="analyzer", name=...)`.
4. Add the class to the optional imports in `wisio/__init__.py` if it depends
   on an extra.

### A new rule

1. Add a key to `KnownRules` in `wisio/rules.py`.
2. Define a `Rule` with a condition and reason templates in `KNOWN_RULES`.
3. Ensure the columns referenced by the condition are computed in the scored
   views (`analysis.set_metric_slope` / predicate columns).
4. Add the key to the documentation in {doc}`../user-guide/bottlenecks` and to
   the user-facing exclusion list.

### A new characteristic

1. Add a key to `KnownCharacteristics`.
2. Subclass `CharacteristicRule`, implement `define_tasks()` and
   `handle_task_results()`.
3. Register the instance in `RuleEngine.process_characteristics()` in
   dependency order.

### A new output

1. Subclass `wisio.output.Output` and implement `handle_result()`.
2. Register a config dataclass and `cs.store(group="output", name=...)`.
3. Add it to `OutputType` and the CLI documentation.

## Performance notes

- The dominant cost is the first read/aggregation pass; later stages operate on
  the much smaller main view.
- Time granularity controls how many `time_range` rows exist: finer buckets
  create more perspectives and more work.
- Logical views add five perspectives per metric and can be significantly
  slower on wide traces.
- Worker memory, not CPU, is usually the limiting resource on large traces;
  see {doc}`../user-guide/clusters`.
