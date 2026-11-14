# Command-line interface

WisIO exposes a single `wisio` command. Configuration is composed with
[Hydra](https://hydra.cc), so any parameter in
{doc}`configuration` can be overridden on the command line without editing
files.

```bash
wisio +analyzer=<name> percentile=<p> trace_path=<path> [overrides...]
```

## Hydra override syntax

| Form | Meaning | Example |
| --- | --- | --- |
| `key=value` | Override an existing key | `percentile=0.99` |
| `group=option` | Select an option from a config group that already has a default | `cluster=slurm`, `output=console` |
| `+group=option` | Add a group that has no default | `+analyzer=recorder` |
| `key.nested=value` | Set a nested key | `analyzer.time_granularity=1e6` |
| `key=[a,b]` | Set a list | `view_types=[file_name,proc_name]` |
| `key=null` | Set a value to null | `percentile=null` |

Two details matter in practice:

- **`analyzer` has no default**, so it must be added with a plus:
  `+analyzer=recorder`. Writing `analyzer=recorder` fails.
- **`cluster` and `output` already have defaults** (`local` and `console`), so
  select them without a plus: `cluster=slurm`, not `+cluster=slurm`.

```{note}
`percentile` and `threshold` cannot both be omitted: the defaults are `None`
and the analyzer raises `ValueError: Either percentile or threshold must be
defined`. Prefer `percentile` for regular use; see
{doc}`../user-guide/analysis`.
```

## Configuration groups

| Group | Options | Select with |
| --- | --- | --- |
| Analyzer | `darshan`, `dftracer`, `recorder` | `+analyzer=<option>` |
| Cluster | `local`, `lsf`, `pbs`, `slurm` | `cluster=<option>` |
| Output | `console` | `output=console` (the default) |

## Getting help

```bash
wisio --help          # Hydra help with the composed configuration
wisio --hydra-help    # Hydra-specific options
wisio --cfg job       # print the fully resolved configuration and exit
wisio --info          # environment, search paths, and plugins
```

`--cfg job` is the quickest way to confirm which values will actually be used,
including defaults from the selected analyzer.

## Examples

### Analyze a Recorder Parquet trace

```bash
wisio +analyzer=recorder percentile=0.99 \
  trace_path=tests/data/extracted/recorder-parquet
```

### Rank by the `time` metric

```bash
wisio +analyzer=dftracer percentile=0.99 metrics=[time] \
  trace_path=/path/to/pfw-traces
```

### Restrict and expand views

```bash
# Only file and process perspectives
wisio +analyzer=recorder percentile=0.99 \
  view_types=[file_name,proc_name] \
  trace_path=/path/to/parquet-traces

# Add logical views (app, node, rank, directory, file pattern)
wisio +analyzer=recorder percentile=0.99 logical_view_types=true \
  trace_path=/path/to/parquet-traces
```

### Exclude rules or characteristics

```bash
wisio +analyzer=recorder percentile=0.99 \
  exclude_bottlenecks=[small_reads,small_writes] \
  exclude_characteristics=[read_xfer_size,write_xfer_size] \
  trace_path=/path/to/parquet-traces
```

The valid keys are listed in {doc}`bottlenecks`.

### Use a different time bucket

```bash
# 100 ms buckets for a DFTracer trace (timestamps are in microseconds)
wisio +analyzer=dftracer percentile=0.99 analyzer.time_granularity=1e5 \
  trace_path=/path/to/pfw-traces
```

```{warning}
The top-level `time_granularity` key exists in the configuration schema but is
not passed to the analyzer. Always set `analyzer.time_granularity`.
```

### Run on a scheduler

```bash
wisio +analyzer=darshan percentile=0.99 \
  cluster=slurm +cluster.n_workers=8 cluster.cores=32 cluster.memory=64GB \
  cluster.job_extra_directives=["--partition=compute","--qos=normal"] \
  trace_path=/path/to/darshan-reports
```

See {doc}`clusters` for the scheduler options.

### Change console output

```bash
wisio +analyzer=recorder percentile=0.99 \
  output.compact=true output.max_bottlenecks=5 output.group_behavior=true \
  trace_path=/path/to/parquet-traces
```

## Run directory

Each invocation creates a Hydra run directory:

```text
outputs/2025-06-08/14-32-07/
├── wisio.log
├── result.html
├── result.txt
├── result.svg
├── bottlenecks/
└── checkpoints/
```

`result.*` are the shareable forms of the console report. To choose a fixed
directory, override Hydra directly:

```bash
wisio ... hydra.run.dir=/scratch/$USER/wisio-run
```

See {doc}`outputs` for the artifacts, and {doc}`configuration` for every
parameter.
