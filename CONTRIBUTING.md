# Contributing to WisIO

First off, thank you for considering contributing to WisIO! We welcome any help to make this tool better.

## How Can I Contribute?

### Reporting Bugs

If you encounter a bug, please report it by opening an issue on our [GitHub Issue Tracker](https://github.com/grc-iit/wisio/issues).

When reporting a bug, please include:
-   A clear and descriptive title.
-   Steps to reproduce the bug.
-   What you expected to happen.
-   What actually happened.
-   Your environment details (e.g., OS, Python version, WisIO version, relevant libraries).

### Suggesting Enhancements

If you have an idea for a new feature or an improvement to an existing one, please open an issue on our [GitHub Issue Tracker](https://github.com/grc-iit/wisio/issues) to discuss it.

Please include:
-   A clear and descriptive title.
-   A detailed description of the proposed enhancement.
-   The use case or problem this enhancement would solve.
-   Any potential benefits or drawbacks.

### Submitting Pull Requests

We love pull requests! If you'd like to contribute code:

1.  **Fork the Repository:** Start by forking the [main WisIO repository](https://github.com/grc-iit/wisio).
2.  **Create a Branch:** Create a new branch in your fork for your changes (e.g., `git checkout -b feature/my-new-feature` or `bugfix/issue-123`).
3.  **Make Your Changes:** Implement your feature or bug fix.
4.  **Test Your Changes:** Ensure your changes pass all tests. You can run tests locally (see "Setting Up a Development Environment" below and refer to the test execution steps in `.github/workflows/ci.yml`).
5.  **Format and Lint:** Ensure your code adheres to our coding standards (see below).
6.  **Commit Your Changes:** Use clear and descriptive commit messages.
7.  **Push to Your Fork:** Push your changes to your forked repository.
8.  **Submit a Pull Request:** Open a pull request from your branch to the `main` branch of the WisIO repository. Provide a clear description of your changes in the PR.

## Coding Standards

We use [Ruff](https://github.com/astral-sh/ruff) for linting and formatting. Please ensure your contributions adhere to these standards. Key configurations (from `pyproject.toml`):
-   Line length: 119 characters
-   Quote style: Preserve existing quotes (`quote-style = "preserve"`)

You can run Ruff locally to check and format your code:
```bash
ruff check .
ruff format .
```

## Setting Up a Development Environment

### Option 1: Dev Container (Recommended)

The repository includes a [dev container](.devcontainer.json) (built from the [Dockerfile](Dockerfile)) with the system dependencies and build tools needed for the C++ components.

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/grc-iit/wisio.git
    ```

2.  **Open in the Container:** In VS Code, use the Dev Containers extension and choose "Reopen in Container".

3.  **Install Python Dependencies (inside the container):**
    ```bash
    python -m pip install --upgrade pip
    # Install WisIO in editable mode with optional extras
    pip install -e .[darshan,dftracer]
    # Install dependencies for tests
    pip install -r tests/requirements.txt
    ```

### Option 2: Manual Setup

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/grc-iit/wisio.git
    cd wisio
    ```

2.  **Create a Python Virtual Environment:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    ```

3.  **Install Python Dependencies:**
    Install WisIO in editable mode along with its optional dependencies (like Darshan and DFTracer support) and dependencies required for running tests.
    ```bash
    python -m pip install --upgrade pip
    # Install Python build dependencies
    pip install meson-python setuptools wheel
    # Install WisIO in editable mode with optional extras
    pip install -e .[darshan,dftracer]
    # Install dependencies for tests
    pip install -r tests/requirements.txt
    ```

4.  **Install System Dependencies (for C++ components):**
    WisIO includes C++ components. To develop these, you'll need system dependencies such as a C++ compiler, CMake, Meson, Ninja, and various development libraries (e.g., `libarrow-dev`, `libhdf5-dev`).
    A comprehensive list and example installation commands for Ubuntu can be found in the "Install system dependencies" step within the `.github/workflows/ci.yml` file.

5.  **Build C++ Components (if making changes to them):**
    When you install WisIO in editable mode (`pip install -e .`), the C++ components are typically built. If you make changes to the C++ source files, you may need to recompile them.
    ```bash
    # Navigate to the build directory (usually created by the editable install)
    # meson compile -C build 
    # Or, if you need to reconfigure and then build:
    # meson setup build --reconfigure -Denable_tests=true -Denable_tools=true
    # meson compile -C build
    ```
    The editable pip install should handle most build aspects, but manual recompilation with Meson might be needed for iterative C++ development.

We look forward to your contributions!
