import altair as alt
import dask
import shutil
import streamlit as st
import numpy as np
import pandas as pd
import tempfile
from wisio import init_with_hydra
from wisio.constants import XFER_SIZE_BIN_LABELS
from wisio.rules import KnownCharacteristics
from wisio.types import Characteristics, RawStats

DEFAULT_THRESHOLD = 45
DEFAULT_TIME_GRANULARITY_IN_SECONDS = 5  # 5 seconds
XFER_SIZE_CAT_TYPE = pd.CategoricalDtype(categories=XFER_SIZE_BIN_LABELS, ordered=True)
VIEW_TYPE_MAPPING = {
    'File': 'file_name',
    'Process': 'proc_name',
    'Timeline': 'time_range',
}

st.set_page_config(
    page_title="WisIO Live",
    layout="centered",
    menu_items={
        'About': 'https://grc.iit.edu/research/projects/wisio',
        'Report a bug': 'https://github.com/grc-iit/wisio/issues',
    },
)

st.write(
    r'''
    <style>
        [data-testid="stImageContainer"] img {border-radius: 0;}
        [data-testid="stMainBlockContainer"] {max-width: 812px;}
    </style>
    ''',
    unsafe_allow_html=True,
)

st.image("assets/logo.png", width=200)
st.title("Welcome to WisIO Live")
st.markdown(
    """
    Analyze, visualize, and understand I/O performance issues in HPC workloads.
    """
)

result = None
bottlenecks = None
characteristics: Characteristics = {}
raw_stats: RawStats = {}

with st.form('analysis_form'):
    trace_files = st.file_uploader(
        "Upload a trace file",
        type=["darshan", "parquet", "pfw", "pfw.gz"],
        accept_multiple_files=True,
    )

    view_types = st.multiselect(
        "Select perspectives to analyze",
        options=VIEW_TYPE_MAPPING.keys(),
        default=VIEW_TYPE_MAPPING.keys(),
    )

    time_granularity = st.slider(
        "Set time granularity for analysis (in seconds)",
        min_value=1,
        max_value=100,
        value=DEFAULT_TIME_GRANULARITY_IN_SECONDS,
        step=1,
        help="This sets the granularity of time intervals for analysis.",
        disabled='Timeline' not in view_types,
    )

    threshold = st.slider(
        "Set the threshold for bottleneck detection",
        min_value=0,
        max_value=90,
        format="%d%%",
        value=DEFAULT_THRESHOLD,
        step=1,
        help="This threshold determines the sensitivity of bottleneck detection.",
    )

    logical_view_types = st.checkbox(
        "Enable logical view types",
        value=False,
        help="Logical view types allow for more complex analysis but may take longer to compute.",
    )

    submit = st.form_submit_button("Analyze")

if submit:
    # Check if all trace files have the same type
    if not trace_files or len(trace_files) == 0:
        st.error("Please upload at least one trace file.")
        st.stop()
    if len(set(file.name.split('.')[-1] for file in trace_files)) > 1:
        st.error("All trace files must be of the same type.")
        st.stop()

    analyzer = 'darshan'
    if all(file.name.endswith('.parquet') for file in trace_files):
        analyzer = 'recorder'
    elif all(file.name.endswith('.pfw') or file.name.endswith('.pfw.gz') for file in trace_files):
        analyzer = 'dftracer'

    with st.status("Analyzing trace files", expanded=True) as status:
        st.write(f"Detected analyzer type: {analyzer.title()}")

        with tempfile.TemporaryDirectory() as temp_dir:
            st.write(f"Using temporary directory: {temp_dir}")

            for trace_file in trace_files:
                with open(f"{temp_dir}/{trace_file.name}", "wb") as temp_trace_file:
                    temp_trace_file.write(trace_file.getbuffer())

            wis = init_with_hydra(
                hydra_overrides=[
                    f"+analyzer={analyzer}",
                    f"analyzer.bottleneck_dir={temp_dir}",
                    f"analyzer.checkpoint={False}",
                    f"analyzer.time_granularity={time_granularity}",
                    f"hydra.run.dir={temp_dir}",
                    f"hydra.runtime.output_dir={temp_dir}",
                    f"logical_view_types={logical_view_types}",
                    f"threshold={threshold}",
                    f"trace_path={temp_dir}",
                    f"view_types=[{','.join([VIEW_TYPE_MAPPING[view_type] for view_type in view_types])}]",
                ]
            )
            st.write("Initialized WisIO analyzer.")

            st.write("Analyzing trace files...")
            result = wis.analyze_trace()
            (bottlenecks, characteristics, raw_stats) = dask.compute(
                result._bottlenecks,
                result.characteristics,
                result.raw_stats,
            )
            st.write("Analysis complete.")

            try:
                st.write("Shutting down analyzer...")
                wis.client.close()
                wis.cluster.close()
                st.write("Analyzer shut down.")
            except Exception as e:
                st.error(f"Error shutting down analyzer: {e}")
                st.write("Please restart the application.")

            st.write("Cleaning up temporary directory...")
            shutil.rmtree(temp_dir, ignore_errors=True)
            st.write("Temporary directory cleaned up.")

            status.update(label="Analysis complete.", expanded=False, state="complete")

            st.session_state['result'] = result
            st.session_state['bottlenecks'] = bottlenecks
            st.session_state['characteristics'] = characteristics
            st.session_state['raw_stats'] = raw_stats

# if 'result' in st.session_state:
#     result = st.session_state['result']
#     bottlenecks = st.session_state['bottlenecks']
#     characteristics = st.session_state['characteristics']
#     raw_stats = st.session_state['raw_stats']
# else:
#     result = None

if result:
    st.subheader("Analysis Results")

    characteristics_tab, bottlenecks_tab = st.tabs(["I/O Characteristics", "I/O Bottlenecks"])

    with characteristics_tab:
        file_count = characteristics[KnownCharacteristics.FILE_COUNT.value].value
        proc_count = characteristics[KnownCharacteristics.PROC_COUNT.value].value
        io_ops = characteristics[KnownCharacteristics.IO_COUNT.value].value
        io_size_fmt = characteristics[KnownCharacteristics.IO_SIZE.value].value_fmt
        io_time = characteristics[KnownCharacteristics.IO_TIME.value].value
        read_xfer_bins = characteristics[KnownCharacteristics.READ_XFER_SIZE.value]._dataframe
        write_xfer_bins = characteristics[KnownCharacteristics.WRITE_XFER_SIZE.value]._dataframe

        col11, col12, col13 = st.columns(3)
        col11.metric("Runtime", f"{raw_stats.job_time:.2f} s", border=True)
        col12.metric(r"\# of Processes", f"{file_count:,}", border=True)
        col13.metric(r"\# of Files", f"{proc_count:,}", border=True)

        col21, col22, col23 = st.columns(3)
        col21.metric("I/O Time", f"{io_time:.2f} s", border=True)
        col22.metric("I/O Operations", f"{io_ops:,}", border=True)
        col23.metric("I/O Size", io_size_fmt, border=True)

        col31, col32 = st.columns(2)
        col31.markdown("**Read Request Size Distribution**")
        read_xfer_bins_full = read_xfer_bins['read_count'].reindex(XFER_SIZE_BIN_LABELS).fillna(0)
        read_xfer_bins_fixed = pd.DataFrame(
            {"Size Range": read_xfer_bins_full.index, "Operations": read_xfer_bins_full.values}
        )
        read_xfer_bins_fixed['Size Range'] = read_xfer_bins_fixed['Size Range'].astype(XFER_SIZE_CAT_TYPE)
        col31.write(
            alt.Chart(read_xfer_bins_fixed)
            .mark_bar()
            .encode(
                x=alt.X('Operations', title='# of I/O Operations'),
                y=alt.Y('Size Range', sort=None, title=None),
            )
        )
        # col31.bar_chart(read_xfer_bins_fixed.set_index('Size Range'), horizontal=True)
        col32.markdown("**Write Request Size Distribution**")
        write_xfer_bins_fixed = write_xfer_bins['write_count'].reindex(XFER_SIZE_BIN_LABELS).fillna(0)
        write_xfer_bins_fixed = pd.DataFrame(
            {"Size Range": write_xfer_bins_fixed.index, "Operations": write_xfer_bins_fixed.values}
        )
        write_xfer_bins_fixed['Size Range'] = write_xfer_bins_fixed['Size Range'].astype(XFER_SIZE_CAT_TYPE)
        col32.write(
            alt.Chart(write_xfer_bins_fixed)
            .mark_bar()
            .encode(
                x=alt.X('Operations', title='# of I/O Operations'),
                y=alt.Y('Size Range', sort=None, title=None),
            )
        )

    with bottlenecks_tab:
        st.write(bottlenecks)

        # st.subheader("Time View (4 bottlenecks with 7 reasons)")

        # with st.expander("[CR1] 32 processes, 2 files, I/O Time: 2.19s (53.26%)"):
        #     st.markdown("""
        #     - **[Excessive metadata access]** Overall **100.00%** (2.19 seconds) of I/O time is spent on metadata access.
        #         - Specifically, **100.00%** (2.19 seconds) is on the 'open' operation.
        #     """)

        # with st.expander("[CR2] 1 process, 6 files, I/O Time: 0.33s (7.97%)"):
        #     st.markdown("""
        #     - **[Excessive metadata access]** Overall **99.35%** (0.33 seconds) of I/O time is spent on metadata access.
        #         - Specifically, **99.13%** (0.33 seconds) is on the 'open' operation.
        #     """)
