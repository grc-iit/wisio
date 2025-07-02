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

st.header("2. Searching for `zindex` library or executable")
st.write("Searching the entire filesystem for any compiled zindex file (`*zindex*.so` or the `zindex` executable). This may take a moment...")

# Use subprocess to run the 'find' command for a more robust search
try:
    with st.spinner("Executing `find / -name '*zindex*.so' -o -name 'zindex'`..."):
        # Search for either the shared library or the executable
        result = subprocess.run(
            ["find", "/", "-name", "*zindex*.so", "-o", "-name", "zindex"],
            capture_output=True,
            text=True,
            timeout=60 # Add a timeout to prevent it from running forever
        )

    st.subheader("Search Results:")
    if result.returncode == 0 and result.stdout:
        found_paths = result.stdout.strip().split('\n')
        st.success(f"Found the following `zindex` related files:")
        st.code('\n'.join(found_paths), language='bash')

        # --- The sys.path trick ---
        st.header("3. Attempting the `sys.path` Trick")
        
        # Try to find a python library file first
        library_file = None
        for path_str in found_paths:
            if path_str.endswith(".so"):
                library_file = Path(path_str)
                break
        
        if library_file:
            # The directory containing the .so file needs to be in the path
            library_dir = library_file.parent
            
            st.write(f"The library was found inside: `{library_dir}`")
            st.write(f"Adding this directory to `sys.path` and attempting to import `zindex_py`...")

            # Add the directory to the path
            sys.path.insert(0, str(library_dir))

            st.subheader("`sys.path` after modification:")
            st.json(sys.path)

            try:
                # The module to import is still zindex_py as defined in the C++ source
                import zindex_py as zindex
                st.success("✅ Successfully imported `zindex_py` after modifying `sys.path`!")
                st.write(f"The imported module is: `{zindex}`")
                st.balloons()
            except ImportError as e:
                st.error(f"❌ Found the .so file but failed to import `zindex_py` even after adding its directory to the path.")
                st.exception(e)
            except Exception as e:
                st.error("An unexpected error occurred during import.")
                st.exception(e)
        else:
            st.warning("Found `zindex` files, but none of them are Python library files (`.so`). Cannot attempt the `sys.path` trick.")


    else:
        st.error("Could not find any `zindex` library or executable anywhere on the filesystem.")
        st.write("This confirms the C++ code is not being compiled at all during the installation.")
        if result.stderr:
            st.subheader("Search command error output:")
            st.code(result.stderr, language='bash')

except subprocess.TimeoutExpired:
    st.error("The file search timed out. The filesystem is likely too large or slow to search completely.")
except Exception as e:
    st.error("An error occurred while trying to search the filesystem.")
    st.exception(e)
