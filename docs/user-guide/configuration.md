# Configuration reference

This page documents the parameters that the `wisio` CLI actually reads. The
schema lives in `wisio/config.py`; when in doubt, `wisio --cfg job` prints the
resolved values for a given command line.

Values are set with Hydra overrides, for example:

```bash
wisio +analyzer=recorder percentile=0.99 \
  metrics=[iops,time] view_types=[file_name,proc_name,time_range] \
  analyzer.time_granularity=1e7 output.max_bottlenecks=10 \
  trace_path=/path/to/parquet-traces
```

```{tip}
`analyzer` must be added with `+analyzer=...` because it has no default.
`cluster` and `output` already have defaults and are selected without a plus.
```

## Core parameters

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `trace_path` | string | *required* | Trace file or directory understood by the selected analyzer. |
| `percentile` | float or null | `null` | Keep views at or above this percentile of the severity score. Mutually exclusive with `threshold`; one of the two is required. |
| `threshold` | int or null | `null` | Slope-based cutoff. For `iops` it is an angle in degrees (0–90); for `time` it is a fraction. Prefer `percentile`. |
| `metrics` | list[str] | `[iops]` | Metrics to rank findings by. Supported values are `iops` and `time`. |
| `view_types` | list[str] | `[time_range, file_name, proc_name]` | Primary perspectives to analyze. Order matters; see {doc}`analysis`. |
| `logical_view_types` | bool | `false` | Also analyze logical views (`app_name`, `node_name`, `rank`, `file_dir`, `file_pattern`). |
| `exclude_bottlenecks` | list[str] | `[]` | Rule keys to skip, e.g. `small_reads`. |
| `exclude_characteristics` | list[str] | `[]` | Characteristic keys to skip, e.g. `read_xfer_size`. |
| `debug` | bool | `false` | Enable debug logging and the debug table in console output. |
| `verbose` | bool | `false` | Print full subject names (files, processes, time periods) in bottleneck descriptions. |

```{warning}
`metrics` accepts only `iops` and `time`. The `Metric` type also names `bw`,
`intensity`, and `att_perf`, but the current scoring path does not compute
them; setting one of those produces no useful findings. `iops` is the default
and the metric used for automated detection.
```

```{warning}
The top-level `time_granularity` key is present in the schema but is **not**
passed to the analyzer. Use `analyzer.time_granularity` instead.
```

## Analyzer parameters

These are common to `darshan`, `dftracer`, and `recorder`.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `analyzer.bottleneck_dir` | string | `${hydra:runtime.output_dir}/bottlenecks` | Where per-view bottleneck records are written. |
| `analyzer.checkpoint` | bool | `true` | Enable checkpointing of intermediate results. |
| `analyzer.checkpoint_dir` | string | `${hydra:runtime.output_dir}/checkpoints` | Checkpoint location. |
| `analyzer.time_approximate` | bool | `true` | Reserved for approximate I/O timing. |
| `analyzer.time_granularity` | float | varies | Width of a time bucket in the analyzer's native timestamp units. |
| `analyzer.view_materialize_max_bytes` | int | `67108864` (64 MiB) | Main views at or below this size are processed in pandas; larger ones stay on Dask. Set to `0` to keep everything on Dask. |

Per-analyzer defaults:

| Analyzer | `analyzer.time_granularity` | Bucket size | Why |
| --- | --- | --- | --- |
| `darshan` | `1e3` | 1 ms | DXT start times are in seconds; the value multiplies them. |
| `dftracer` | `1e6` | 1 s | DFTracer timestamps are in microseconds. |
| `recorder` | `1e7` | 10 ms | Recorder `tmid` values are in nanoseconds. |

```bash
# Coarser buckets reduce the number of time periods and speed up analysis.
wisio +analyzer=recorder percentile=0.99 analyzer.time_granularity=1e8 ...
```

## Output parameters

The default output group is `console`. Common options:

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `output.compact` | bool | `false` | Use shortened descriptions and subject names. |
| `output.group_behavior` | bool | `false` | Group findings with similar I/O behavior. |
| `output.name` | string | `""` | Optional label prefixed to output panels. |
| `output.root_only` | bool | `true` | Show only top-level (depth-1) perspectives. |
| `output.view_names` | list[str] | `[]` | Restrict output to specific view names. When non-empty, this takes precedence over `root_only`. |

Console-specific options:

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `output.max_bottlenecks` | int | `3` | Maximum findings to display per view. |
| `output.show_debug` | bool | `false` | Include the throughput/retention/severity debug table. |
| `output.show_characteristics` | bool | `true` | Print the I/O Characteristics panel. |
| `output.show_header` | bool | `true` | Print panel titles. |

## Cluster parameters

The default is a local Dask cluster. See {doc}`clusters` for guidance.

### Common

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `cluster.local_directory` | string | `/tmp/${hydra:job.name}/${hydra:job.id}` | Worker temporary directory. |

### `cluster=local`

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `cluster.host` | string or null | `null` | Scheduler host. |
| `cluster.memory_limit` | int or null | `null` | Memory limit per worker, in bytes. `null` lets Dask decide. |
| `cluster.n_workers` | int or null | `null` | Number of workers. `null` uses Dask's default. |
| `cluster.processes` | bool | `true` | Use worker processes rather than threads. |
| `cluster.silence_logs` | int | `50` (`CRITICAL`) | Log level for Dask's own logs. |

### `cluster=lsf`, `cluster=pbs`, `cluster=slurm`

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `+cluster.n_workers` | int | `0` | Number of Dask workers (jobs) to request. Add it with a plus because it is not part of the job-queue schema. |
| `cluster.cores` | int | `16` | Cores requested per job. |
| `cluster.processes` | int | `1` | Worker processes per job. |
| `cluster.memory` | string or null | `null` | Memory per job, e.g. `64GB`. |
| `cluster.death_timeout` | int | `60` | Seconds before a silent worker is considered dead. |
| `cluster.log_directory` | string | `""` | Directory for scheduler job logs. |
| `cluster.job_directives_skip` | list[str] | `[]` | Job script directives to drop. |
| `cluster.job_extra_directives` | list[str] | `[]` | Extra scheduler directives, e.g. `["--partition=compute"]`. |
| `cluster.scheduler_options.host` | string | current hostname | Address the Dask scheduler binds to. |
| `cluster.scheduler_options.dashboard_address` | string or null | `null` | Dask dashboard address, e.g. `:8787`. |

LSF adds:

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `cluster.use_stdin` | bool | `true` | Pass the job script through stdin. |

## Hydra jobs and logging

WisIO customizes Hydra's job name and logging:

| Setting | Value |
| --- | --- |
| Job name | `wisio` |
| Run directory | `outputs/<date>/<time>/` (Hydra default) |
| Log file | `${hydra:runtime.output_dir}/wisio.log` |
| Root log level | `INFO` |

Override the run directory directly when you need a stable location:

```bash
wisio +analyzer=recorder percentile=0.99 \
  hydra.run.dir=/scratch/$USER/wisio-run \
  trace_path=/path/to/parquet-traces
```

## Complete example

```bash
wisio +analyzer=dftracer \
  trace_path=/scratch/traces/bert \
  percentile=0.99 \
  metrics=[iops] \
  view_types=[time_range,file_name,proc_name] \
  logical_view_types=true \
  exclude_bottlenecks=[small_reads] \
  analyzer.checkpoint=true \
  analyzer.time_granularity=1e6 \
  analyzer.view_materialize_max_bytes=0 \
  cluster=slurm \
  +cluster.n_workers=8 \
  cluster.cores=32 \
  cluster.memory=64GB \
  cluster.job_extra_directives=["--partition=compute"] \
  output.compact=true \
  output.max_bottlenecks=5
```
