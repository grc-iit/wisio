import papermill as pm

checkpoint_dir = "/usr/workspace/iopp/wisio_logs/_checkpoints"

traces = [
    # (
    #     "dftracer",
    #     "bert-v100-node-4-v1",
    #     "/p/lustre3/iopp/dftracer-traces-lfs/v1.0.5-develop/corona/bert/v100/node-4/v1/COMPACT/*.pfw.gz",
    # ),
    # (
    #     "dftracer",
    #     "bert-v100-node-16-v3",
    #     "/p/lustre3/iopp/dftracer-traces-lfs/v1.0.5-develop/corona/bert/v100/node-16/v3/COMPACT/*.pfw.gz",
    # ),
    # (
    #     "dftracer",
    #     "cm1-node-1",
    #     "/p/lustre3/iopp/dftracer-traces-lfs/v1.0.5-develop/corona/cm1/APP/node-1/v1/COMPACT/*.pfw.gz",
    # ),
    # (
    #     "dftracer",
    #     "cm1-node-32",
    #     "/p/lustre3/iopp/dftracer-traces-lfs/v1.0.5-develop/corona/cm1/APP/node-32/v1/COMPACT/*.pfw.gz",
    # ),
    # (
    #     "dftracer",
    #     "cosmoflow-dlio-v100-node-4-v1",
    #     "/p/lustre3/iopp/dftracer-traces-lfs/v1.0.5-develop/corona/cosmoflow/dlio-v100/node-4/v1/COMPACT/*.pfw.gz",
    # ),
    # (
    #     "dftracer",
    #     "cosmoflow-dlio-v100-node-16-v3",
    #     "/p/lustre3/iopp/dftracer-traces-lfs/v1.0.5-develop/corona/cosmoflow/dlio-v100/node-16/v3/COMPACT/*.pfw.gz",
    # ),
    # (
    #     "dftracer",
    #     "montage-pegasus-dss-2deg-node-4",
    #     "/p/lustre3/iopp/dftracer-traces-lfs/v1.0.5-develop/corona/montage/pegasus-dss-2deg/node-4/v1/COMPACT/*.pfw.gz",
    # ),
    # (
    #     "dftracer",
    #     "montage-pegasus-dss-2deg-node-16",
    #     "/p/lustre3/iopp/dftracer-traces-lfs/v1.0.5-develop/corona/montage/pegasus-dss-2deg/node-16/v1/COMPACT/*.pfw.gz",
    # ),
    # (
    #     "dftracer",
    #     "resnet50-dlio-v100-node-4-v1",
    #     "/p/lustre3/iopp/dftracer-traces-lfs/v1.0.5-develop/corona/resnet50/dlio-v100/node-4/v1/COMPACT/*.pfw.gz",
    # ),
    # (
    #     "dftracer",
    #     "resnet50-dlio-v100-node-16-v3",
    #     "/p/lustre3/iopp/dftracer-traces-lfs/v1.0.5-develop/corona/resnet50/dlio-v100/node-16/v3/COMPACT/*.pfw.gz",
    # ),
    # /p/lustre3/iopp/dftracer-traces-lfs/v1.0.5-develop/corona/unet3d/dlio-v100/node-1/v1/RAW
    # (
    #     "dftracer",
    #     "unet3d-dlio-v100-node-1-v1",
    #     "/p/lustre3/iopp/dftracer-traces-lfs/v1.0.5-develop/corona/unet3d/dlio-v100/node-1/v1/RAW/*.pfw.gz",
    # ),
    (
        "dftracer",
        "unet3d-dlio-v100-node-16-v2",
        "/p/lustre3/iopp/dftracer-traces-lfs/v1.0.5-develop/corona/unet3d/dlio-v100/node-16/v2/RAW/*.pfw.gz",
    ),
    # (
    #     "dftracer",
    #     "deepspeed-dlio-node-16",
    #     f"{dftracer_trace_dir.replace('traces-lfs', 'traces')}/megatron_deepspeed-1_16_8/megatron_deepspeed-1_16_8-COMPACT/*.pfw.gz",
    # ),
    # (
    #     "dftracer",
    #     "deepspeed-dlio-scr-node-16",
    #     f"{dftracer_trace_dir.replace('traces-lfs', 'traces')}/megatron_deepspeed-1-100-1_16_8_scr/megatron_deepspeed-1-100-1_16_8_scr-COMPACT/*.pfw.gz",
    # ),
    (
        "dftracer",
        "1000-genome-pegasus-node-32",
        "/p/lustre3/iopp/dftracer-traces-lfs/v1.0.5-develop/corona/1000-genome/pegasus/node-32/v1/COMPACT/*.pfw.gz",
    ),
]

for analyzer, trace_name, trace_path in traces:
    pm.execute_notebook(
        "analysis.ipynb",
        f"analysis-{analyzer}-{trace_name}.ipynb",
        parameters=dict(
            analyzer=analyzer,
            checkpoint=True,
            checkpoint_dir=f"{checkpoint_dir}/{analyzer}-{trace_name}",
            logical_view_types=False,
            output_max_bottlenecks=1,
            output_root_only=False,
            run_dir=f".wisio/{analyzer}/{trace_name}",
            percentile=0.99,
            trace_path=trace_path,
        ),
    )

# bert (4 node - 8 GPUs per node = 32 processes)
# 1000 steps
# every step reads 48 images/samples of 2500 bytes each
# https://github.com/llnl-asr/iopp/blob/system/corona/apps/dlio/script.sh
# do `prefetch_size` of 4GB
