# Bottlenecks and characteristics

WisIO reports two kinds of results:

- **Bottlenecks** — scored rows from a perspective that are worth investigating,
  each with a severity and one or more reasons.
- **I/O characteristics** — workload-level summary statistics that describe the
  trace as a whole.

Both are driven by rules in `wisio/rules.py`.

## Bottleneck rules

A bottleneck rule has a condition over a view row and one or more reason
templates. A row is reported when its condition is true; each reason whose own
condition is true is attached to the finding.

| Key | Name | Condition | Reasons describe |
| --- | --- | --- | --- |
| `excessive_metadata_access` | Excessive metadata access | `metadata_time / time >= 0.5` | Whether `open`, `close`, or `seek` dominates the metadata time |
| `operation_imbalance` | Operation imbalance | `abs(write_count - read_count) / count > 0.1` | Whether reads or writes dominate the operation count |
| `random_operations` | Random operations | `random_count / count > 0.5` | Share of random operations |
| `size_imbalance` | Size imbalance | `size > 0 and abs(write_size - read_size) / size > 0.1` | Whether reads or writes dominate the transferred bytes |
| `small_reads` | Small reads | `read_time / time > 0.5 and read_size / count < 1 MiB` | Read time share and average read size |
| `small_writes` | Small writes | `write_time / time > 0.5 and write_size / count < 1 MiB` | Write time share and average write size |

All quantities are evaluated per view row. For example, in a
`(proc_name, file_name)` view, `read_time` is the read time of one process on
one file, and `time` is that row's total I/O time.

### Reading a finding

```text
[CR1] 32 processes access 2 files within 1 time period (5) across 32 I/O
operations and have an I/O time of 2.19 seconds which is 53.26% of overall
I/O time of the workload.
└── [Excessive metadata access] Overall 100.00% (2.19 seconds) of I/O time is
    spent on metadata access, specifically 100.00% (2.19 seconds) on the
    'open' operation.
```

- `CR` is the severity code; `1` is the finding's index within its table.
- The first line describes the *scope*: how many processes/files/time periods
  are involved, how many operations, and the I/O time as a share of the
  workload.
- Indented lines are **reasons** produced by the rule. A finding may have up to
  five reasons (`MAX_REASONS`); if none of the reason conditions match, WisIO
  says *"No reason found, further investigation needed."*

Use `verbose=true` to list the actual process, file, and time-period names
instead of just counts, and `output.compact=true` for shorter descriptions.

### Under slope-based scoring

When the `iops` metric is used, a finding can be worth a small fraction of the
total I/O time and still rank critical. In that case the description adds why:

```text
It takes 10.4x as much of the I/O time as its share of operations.
```

That ratio is `1 / iops_slope`; see {doc}`analysis`.

## Excluding rules

Pass the rule keys to skip them:

```bash
wisio percentile=0.99 \
  exclude_bottlenecks=[small_reads,small_writes] \
  trace_path=...
```

Valid keys: `excessive_metadata_access`, `operation_imbalance`,
`random_operations`, `size_imbalance`, `small_reads`, `small_writes`.

## I/O characteristics

Characteristics summarize the whole analyzed trace. They appear in the first
console panel and in the web app.

| Key | Panel label | Description |
| --- | --- | --- |
| `access_pattern` | Access Pattern | Sequential vs random operation counts and shares. |
| `app_count` | Apps | Number of distinct applications parsed from process names. |
| `complexity` | Complexity | `log10(processes × time periods × files)`; a rough search-space size. |
| `file_count` | Files | Distinct files, split into shared and file-per-process (FPP) files. |
| `io_count` | I/O Operations | Total operations, split into read, write, and metadata. |
| `io_size` | I/O Size | Total bytes, split into read and write. |
| `io_time` | I/O Time | I/O time of the slowest process (or total when there is no process view), split into read/write/metadata. |
| `node_count` | Nodes | Distinct hosts parsed from process names. |
| `proc_count` | Processes/Ranks | Distinct process identifiers. |
| `read_xfer_size` | Read Requests | Histogram of read sizes over fixed bins (<4 KiB … >64 MiB). |
| `write_xfer_size` | Write Requests | Histogram of write sizes over the same bins. |
| `time_period` | Time Periods | Number of distinct time buckets, with the configured granularity. |

**Shared vs FPP files.** A file is *FPP* (file-per-process) when exactly one
process accesses it. Files accessed by more than one process are *shared*.
A high FPP share usually means the application is writing one file per rank;
a high shared share means coordination or contention is more likely.

**Transfer-size bins.** Read and write requests are bucketed at 4 KiB, 16 KiB,
64 KiB, 256 KiB, 1 MiB, 4 MiB, 16 MiB, and 64 MiB, matching the bins in
`wisio/constants.py`.

Exclude characteristics with:

```bash
wisio percentile=0.99 \
  exclude_characteristics=[read_xfer_size,write_xfer_size] \
  trace_path=...
```

Valid keys are the table's first column.

## Where the numbers go

The bottleneck records are written to `analyzer.bottleneck_dir` as Parquet and
then rendered by the output layer. See {doc}`outputs`.
