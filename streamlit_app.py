import streamlit as st
import sys
import os
from pathlib import Path
import subprocess

st.set_page_config(layout="wide")

st.title("Installation & Path Debugger")

st.header("1. Python's Search Path (`sys.path`)")
st.write("This is the list of directories where Python looks for modules to import.")
st.json(sys.path)

st.header("2. Searching for `zindex_py` library")
st.write("Searching the entire filesystem for the compiled library (`*zindex_py*.so`). This may take a moment...")

# Use subprocess to run the 'find' command for a more robust search
try:
    with st.spinner("Executing `find / -name '*zindex_py*.so'`..."):
        result = subprocess.run(
            ["find", "/", "-name", "*zindex_py*.so"],
            capture_output=True,
            text=True,
            timeout=60 # Add a timeout to prevent it from running forever
        )

    st.subheader("Search Results:")
    if result.returncode == 0 and result.stdout:
        found_paths = result.stdout.strip().split('\n')
        st.success(f"Found the library at the following locations:")
        st.code('\n'.join(found_paths), language='bash')

        # --- The sys.path trick ---
        st.header("3. Attempting the `sys.path` Trick")
        
        library_path_to_try = None
        for path_str in found_paths:
            # Heuristic: prefer a path that looks like a library directory
            if 'lib' in path_str.lower() or 'site-packages' in path_str.lower():
                library_path_to_try = Path(path_str)
                break
        
        if not library_path_to_try:
            library_path_to_try = Path(found_paths[0])

        # The directory containing the .so file needs to be in the path
        library_dir = library_path_to_try.parent
        
        st.write(f"The library was found inside: `{library_dir}`")
        st.write(f"Adding this directory to `sys.path` and attempting to import `zindex_py`...")

        # Add the directory to the path
        sys.path.insert(0, str(library_dir))

        st.subheader("`sys.path` after modification:")
        st.json(sys.path)

        try:
            import zindex_py as zindex
            st.success("✅ Successfully imported `zindex_py` after modifying `sys.path`!")
            st.write(f"The imported module is: `{zindex}`")
            st.balloons()
        except ImportError as e:
            st.error(f"❌ Failed to import `zindex_py` even after adding its directory to the path.")
            st.exception(e)
        except Exception as e:
            st.error("An unexpected error occurred during import.")
            st.exception(e)

    else:
        st.error("Could not find the `zindex_py` library anywhere on the filesystem.")
        st.write("This confirms the library is not being built or installed correctly.")
        if result.stderr:
            st.subheader("Search command error output:")
            st.code(result.stderr, language='bash')

except subprocess.TimeoutExpired:
    st.error("The file search timed out. The filesystem is likely too large or slow to search completely.")
except Exception as e:
    st.error("An error occurred while trying to search the filesystem.")
    st.exception(e)

