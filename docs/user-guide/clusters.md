# Running on clusters

WisIO analyzes traces with [Dask](https://www.dask.org/). The default is a
local cluster sized by Dask; on an HPC system you can submit workers through
LSF, PBS, or SLURM instead.

## Local cluster (default)

```bash
wisio +analyzer=recorder percentile=0.99 trace_path=/path/to/traces
```

Useful local options:

```bash
wisio +analyzer=recorder percentile=0.99 \
  cluster.n_workers=4 \
  cluster.memory_limit=8000000000 \
  cluster.processes=true \
  trace_path=/path/to/traces
```

| Option | Default | Notes |
| --- | --- | --- |
| `cluster.n_workers` | Dask default | More workers help multi-view analyses, at the cost of memory. |
| `cluster.memory_limit` | `null` | Bytes per worker; `null` lets Dask use the available memory. |
| `cluster.processes` | `true` | `false` runs workers as threads (lighter, but more memory growth on large traces). |
| `cluster.local_directory` | `/tmp/wisio/<job-id>` | Spill directory for workers. |
| `cluster.silence_logs` | `50` (`CRITICAL`) | Raising this to `10` shows Dask worker logs. |

```{tip}
If a large trace gets workers killed, increase `cluster.memory_limit` or
reduce `cluster.n_workers`. The main view is partitioned across workers, so
adding workers does not reduce the total memory required; each worker still
needs enough room for the partitions it holds.
```

## Job-queue clusters

Select the scheduler group with `cluster=`:

```bash
wisio +analyzer=darshan percentile=0.99 \
  cluster=slurm \
  +cluster.n_workers=8 \
  cluster.cores=16 \
  cluster.memory=64GB \
  cluster.job_extra_directives=["--partition=compute","--qos=normal"] \
  trace_path=/path/to/darshan-reports
```

```{important}
`n_workers` is not part of the job-queue configuration schema (only the local
cluster has it), so add it with a plus: **`+cluster.n_workers=8`**. Without it
the Dask job-queue cluster starts zero workers and the analysis waits forever.
```

The same pattern works for LSF and PBS:

```bash
# LSF
wisio ... cluster=lsf +cluster.n_workers=8 cluster.cores=16 cluster.memory=64GB

# PBS
wisio ... cluster=pbs +cluster.n_workers=8 cluster.cores=32 cluster.memory=128GB
```

| Option | Default | Notes |
| --- | --- | --- |
| `+cluster.n_workers` | `0` | Number of Dask workers (jobs) to request. **Required in practice.** |
| `cluster.cores` | `16` | Cores per job. |
| `cluster.processes` | `1` | Worker processes per job. |
| `cluster.memory` | `null` | Memory per job, e.g. `64GB`. |
| `cluster.death_timeout` | `60` | Seconds before an unresponsive worker is replaced. |
| `cluster.job_directives_skip` | `[]` | Directives to remove from generated job scripts. |
| `cluster.job_extra_directives` | `[]` | Extra scheduler directives. |
| `cluster.log_directory` | `""` | Where scheduler job logs are written. |
| `cluster.scheduler_options.host` | current hostname | Interface the Dask scheduler advertises. |
| `cluster.scheduler_options.dashboard_address` | `null` | Set to e.g. `:8787` or `host:8787` to expose the Dask dashboard. |

LSF additionally supports:

| Option | Default | Notes |
| --- | --- | --- |
| `cluster.use_stdin` | `true` | Submit the job script via stdin. |

### Scheduler host and networking

The Dask scheduler runs in the `wisio` process on the submitting node. Worker
jobs must be able to reach it, so `cluster.scheduler_options.host` should be
an address reachable from the compute nodes. It defaults to the submitting
host's hostname; on systems with a separate management network, set it
explicitly:

```bash
cluster.scheduler_options.host=$(hostname -f)
```

## Checkpoints and scratch space

Checkpoints are written by the client process, not by workers, so
`analyzer.checkpoint_dir` can stay on the submit node. The trace itself and
`cluster.local_directory` must be visible to the workers.

On a shared filesystem, prefer a per-run scratch directory:

```bash
wisio +analyzer=dftracer percentile=0.99 \
  cluster=slurm +cluster.n_workers=8 \
  cluster.local_directory=/scratch/$USER/wisio/$SLURM_JOB_ID \
  analyzer.checkpoint_dir=/scratch/$USER/wisio/checkpoints \
  hydra.run.dir=/scratch/$USER/wisio/run \
  trace_path=/scratch/traces/bert
```

## Choosing resources

- **Small traces** (a few hundred MB): the local cluster is faster than
  waiting in a queue.
- **Many perspectives**: more workers help because each perspective is an
  independent Dask task. Worker memory, not CPU, is usually the limit.
- **Very large traces**: keep `analyzer.view_materialize_max_bytes` at its
  default (or `0` to force Dask) and give each worker enough memory for one
  main-view partition.
- **Repeated experiments**: keep `analyzer.checkpoint=true` and reuse the
  checkpoint directory to skip the expensive read/aggregate stages.

See {doc}`configuration` for the full parameter tables.
