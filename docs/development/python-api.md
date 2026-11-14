# Python API

WisIO is primarily a CLI, but the same pipeline is available from Python. The
API is small and still pre-1.0, so treat the signatures below as the supported
surface and the classes in `wisio.analyzer` / `wisio.output` as extension
points.

## `init_with_hydra`

```python
from wisio import init_with_hydra

wis = init_with_hydra([
    "+analyzer=recorder",
    "percentile=0.99",
    "trace_path=/path/to/parquet-traces",
    "cluster.n_workers=2",
    "hydra.run.dir=/tmp/wisio-run",
])
```

`init_with_hydra(overrides: list[str]) -> WisIOInstance` composes the same Hydra
configuration as the CLI and instantiates:

| Attribute | Type | Description |
| --- | --- | --- |
| `analyzer` | `Analyzer` | Reader/analyzer selected by `+analyzer=...` |
| `client` | `dask.distributed.Client` | Client connected to the cluster |
| `cluster` | Dask cluster | Local or job-queue cluster |
| `hydra_config` | `DictConfig` | Resolved configuration |
| `output` | `Output` | Output implementation (console by default) |

The overrides use exactly the same syntax as the CLI, including the required
`+` for `analyzer`.

## `WisIOInstance.analyze_trace`

```python
result = wis.analyze_trace()
```

This calls the analyzer with the values already in `hydra_config`
(`trace_path`, `metrics`, `view_types`, exclusions, ...). Three parameters can
be overridden per call:

```python
result = wis.analyze_trace(
    percentile=0.99,
    threshold=None,
    view_types=["file_name", "proc_name"],
)
```

`result` is an `AnalyzerResultType`:

| Field | Description |
| --- | --- |
| `characteristics` | Workload-level `RuleResult` records |
| `raw_stats` | Runtime, time granularity, and raw record count |
| `bottleneck_rules` | `BottleneckRule` instances used for this run |
| `bottleneck_dir` | Directory containing the bottleneck Parquet files |
| `view_results` | Per-metric, per-perspective `ViewResult` objects |
| `evaluated_views` | Scored views |
| `main_view` | Aggregated main view |
| `metric_boundaries` | Numeric boundaries used for scoring |
| `_bottlenecks` | Lazy Dask DataFrame of all findings |

`characteristics`, `raw_stats`, and `_bottlenecks` are lazy. Resolve them with
`dask.compute` before inspecting values:

```python
import dask

bottlenecks, characteristics, raw_stats = dask.compute(
    result._bottlenecks,
    result.characteristics,
    result.raw_stats,
)
```

## Full example

```python
import dask
from wisio import init_with_hydra

wis = init_with_hydra([
    "+analyzer=recorder",
    "percentile=0.99",
    "metrics=[iops]",
    "view_types=[time_range,file_name,proc_name]",
    "trace_path=/path/to/parquet-traces",
    "hydra.run.dir=/tmp/wisio-run",
])

try:
    result = wis.analyze_trace()

    # Render and save result.html / result.txt / result.svg.
    wis.output.handle_result(metrics=wis.hydra_config.metrics, result=result)

    bottlenecks, characteristics, raw_stats = dask.compute(
        result._bottlenecks,
        result.characteristics,
        result.raw_stats,
    )
    print(f"{len(bottlenecks):,} findings")
finally:
    # Always close the client before the cluster: workers outlive the call
    # otherwise, and later runs start on top of them.
    wis.client.close()
    wis.cluster.close()
```

## `Analyzer.analyze_trace`

If you are writing your own reader, subclass `wisio.analyzer.Analyzer`:

```python
from wisio.analyzer import Analyzer

class MyAnalyzer(Analyzer):
    def read_trace(self, trace_path: str):
        # Return a Dask DataFrame with the common columns documented in
        # docs/development/architecture.md.
        ...
```

The base class provides the full analysis pipeline; implement `read_trace()`
and, if needed, `postread_trace()`, `read_stats()`, or `compute_job_time()`.
Register the class in `wisio/config.py` so `+analyzer=<name>` resolves it.

When constructing an analyzer directly (outside Hydra), pass non-empty
`bottleneck_dir` and `checkpoint_dir` if checkpointing is enabled, ensure a
Dask client is running, and call:

```python
result = analyzer.analyze_trace(
    trace_path="...",
    percentile=0.99,
    metrics=["iops"],
    view_types=["time_range", "file_name", "proc_name"],
)
```

```{note}
`accuracy` appears in the `Analyzer.analyze_trace` signature for historical
reasons but is not used by the CLI. `percentile` and `threshold` are mutually
exclusive in practice; provide one.
```

## Output API

`wisio.output.ConsoleOutput` is the supported output. It reads the bottleneck
Parquet directory referenced by `result.bottleneck_dir` and writes the artifacts
into Hydra's runtime output directory. See {doc}`../user-guide/outputs`.

## Stability

WisIO is at `0.x`. The CLI and configuration keys are the most stable surface;
the Python dataclasses may change between releases. If you build on the API,
pin a version and check the release notes.
