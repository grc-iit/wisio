# Interactive analysis (notebooks)

The `notebooks/` directory contains Jupyter workflows for exploring a trace
interactively. They drive the same analyzer API as the CLI but keep the
intermediate data in the kernel, so you can inspect views, plot distributions,
and iterate on parameters without re-running the whole pipeline.

Use notebooks when you want to:

- inspect the aggregated main view or one specific perspective,
- prototype a rule, a metric, or a figure,
- run the same analysis over a list of traces with Papermill.

For the browser front end, see {doc}`web-app`.

## Setup

Notebooks are not installed with the package; run them from a repository
checkout.

```bash
git clone https://github.com/grc-iit/wisio.git
cd wisio

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\Activate.ps1

# Runtime dependencies plus the reader you need.
pip install -e .[dftracer]       # add [darshan] for Darshan; recorder needs no extra

# Notebook tooling.
pip install jupyterlab
pip install -r notebooks/requirements.txt
```

`notebooks/requirements.txt` installs Papermill, `ipykernel`, and autotime.
If an editable install causes Hydra's plugin discovery to fail on your
platform, use a non-editable `pip install .[dftracer]` instead (see
{doc}`../project/faq`).

## Open the maintained notebook

```bash
jupyter lab notebooks/analysis.ipynb
```

`analysis.ipynb` is the current, maintained entry point. Many other notebooks
in `notebooks/` are exploratory artifacts from paper runs; they may use older
APIs and hard-coded lab paths. Start from `analysis.ipynb`.

The first cells add the repository root to `sys.path`:

```python
import os
import sys

sys.path.append(os.path.abspath("../"))
```

Jupyter starts the kernel with the notebook directory as the working directory,
so `../` is the repository root. Keep the notebook in `notebooks/` or adjust
the path.

## Parameters

Edit the parameter cell before running:

| Parameter | Default / meaning |
| --- | --- |
| `analyzer` | `"dftracer"`; also `"darshan"` or `"recorder"` |
| `trace_path` | A lab-specific path in the template; point it at your trace file or directory |
| `percentile` | `0.95`; the same percentile selection the CLI uses |
| `checkpoint` | `True`; reuse intermediate results between runs |
| `logical_view_types` | `False`; enable app/node/rank/directory/pattern views |
| `output_max_bottlenecks` | `1`; findings shown per view in the console panel |
| `output_root_only` | `False`; also show nested perspectives |
| `run_dir` | `.wisio/<analyzer>/<timestamp>`; artifacts and checkpoints |

`bottleneck_dir` and `checkpoint_dir` are derived from `run_dir`.

The setup cell composes the same Hydra configuration as the CLI:

```python
with initialize(version_base=None, config_path=None):
    init_hydra_config_store()
    cfg = compose(
        config_name="config",
        overrides=[
            f"+analyzer={analyzer}",
            f"analyzer.bottleneck_dir={bottleneck_dir}",
            f"analyzer.checkpoint={checkpoint}",
            f"analyzer.checkpoint_dir={checkpoint_dir}",
            f"hydra.run.dir={run_dir}",
            f"hydra.runtime.output_dir={run_dir}",
            f"logical_view_types={logical_view_types}",
            f"output.max_bottlenecks={output_max_bottlenecks}",
            f"output.root_only={output_root_only}",
            f"percentile={percentile}",
            f"trace_path={trace_path}",
        ],
        return_hydra_config=True,
    )
    HydraConfig.instance().set_config(cfg)
    cluster = instantiate(cfg.cluster)
    client = Client(cluster)
    analyzer = instantiate(cfg.analyzer)
    output = instantiate(cfg.output)
```

Add any CLI override to this list — `metrics=[time]`,
`view_types=[file_name,proc_name]`, `cluster=slurm`,
`+cluster.n_workers=8`, and so on. The options are the same as
{doc}`configuration`.

## Run and explore

The next cells run the analysis and render the console report:

```python
result = analyzer.analyze_trace(
    trace_path=cfg.trace_path,
    exclude_bottlenecks=cfg.exclude_bottlenecks,
    exclude_characteristics=cfg.exclude_characteristics,
    logical_view_types=cfg.logical_view_types,
    metrics=cfg.metrics,
    percentile=cfg.percentile,
    view_types=cfg.view_types,
)

output.handle_result(metrics=cfg.metrics, result=result)
```

`result.html`, `result.txt`, `result.svg`, `bottlenecks/`, and `checkpoints/`
are written under `run_dir`. The `result` object also exposes the intermediate
data:

| Attribute | Contents |
| --- | --- |
| `result.main_view` | Aggregated main view |
| `result.view_results[metric][view_key].view` | One perspective |
| `result.evaluated_views` | Scored views |
| `result.characteristics` | Workload summaries |
| `result.raw_stats` | Runtime, granularity, raw record count |
| `result._bottlenecks` | Lazy DataFrame of findings |

These are Dask objects; resolve them with `.compute()` or `dask.compute(...)`.
For example, inspect the slowest files in the `(time_range, file_name)` view:

```python
view = result.view_results["iops"][("time_range", "file_name")].view
slowest = view.compute().sort_values("time", ascending=False)
slowest.head(20)
```

Close the cluster when you are done with the notebook:

```python
client.close()
cluster.close()
```

## Batch runs with Papermill

`notebooks/analysis.py` executes `analysis.ipynb` once per trace through
Papermill. Edit the `traces` list and `checkpoint_dir` (the template contains
lab paths), then run it from the notebook directory:

```bash
cd notebooks
python analysis.py
```

It writes `analysis-<analyzer>-<trace-name>.ipynb` with the outputs embedded.
Reuse a `checkpoint_dir` per trace to avoid recomputing the main view.

```{note}
The `cluster_config_local.yml` and `cluster_config_lsf.yml` files in
`notebooks/` are from an older cluster-manager API. The maintained notebook
configures Dask through the Hydra overrides shown above.
```

## Notebook map

| Path | Purpose |
| --- | --- |
| `analysis.ipynb` | Maintained end-to-end workflow |
| `analysis.py` | Papermill batch wrapper |
| `analysis-dftracer-*.ipynb` | Per-application DFTracer case studies |
| `recorder-*.ipynb` | Recorder case studies |
| `evals/` | Evaluation experiments |
| `pocs/` | Early proofs of concept |
| `artifacts/` | Figure and artifact generation |
| `flamegraphs/` | Flamegraph SVG/text artifacts |

Most case-study notebooks contain hard-coded paths from the paper's runs; use
them as examples of what can be plotted, not as a stable interface.

## Notebooks vs CLI vs web

| | Notebooks | CLI | WisIO Web |
| --- | --- | --- | --- |
| Best for | Exploration and custom figures | Repeatable runs and clusters | Quick browser uploads |
| Intermediate data | Available in the kernel | No | No |
| Batch runs | Papermill | Shell loops | No |
| Maximum trace size | Your machine/cluster | Your cluster | 20 MB |

See {doc}`web-app` for the browser interface.
