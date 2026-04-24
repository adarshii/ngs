# 🤝 Contributing to the NGS WGS Variant-Calling Pipeline

Thank you for considering a contribution! All contributions are welcome: bug reports,
feature suggestions, documentation improvements, and code changes.

---

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Reporting Bugs](#reporting-bugs)
3. [Suggesting Features](#suggesting-features)
4. [Development Workflow](#development-workflow)
5. [Code Style](#code-style)
6. [Running Tests](#running-tests)
7. [Pull Request Process](#pull-request-process)

---

## Code of Conduct

Be respectful and constructive. We follow the
[Contributor Covenant v2.1](https://www.contributor-covenant.org/version/2/1/code_of_conduct/).

---

## Reporting Bugs

1. Search [existing issues](https://github.com/adarshii/ngs/issues) first.
2. Open a new issue and include:
   - **Description** — what went wrong and what you expected.
   - **Reproduction steps** — minimal commands to reproduce the bug.
   - **Environment** — OS, Python version, Snakemake version, conda environment
     (`conda list`).
   - **Error output** — full traceback or log snippet.

---

## Suggesting Features

Open a GitHub Issue with the label **`enhancement`** and describe:
- The use-case / scientific motivation.
- A rough API or workflow sketch if relevant.

---

## Development Workflow

```bash
# 1. Fork the repository and clone your fork
git clone https://github.com/<your-username>/ngs.git
cd ngs

# 2. Create a feature branch
git checkout -b feature/my-new-feature

# 3. Create and activate the conda environment
conda env create -f environment.yaml
conda activate ngs-pipeline

# 4. Install the package in editable mode with dev extras
pip install -e ".[dev]"

# 5. Make your changes, then run the tests
pytest tests/ -v

# 6. Commit and push
git add .
git commit -m "feat: short description"
git push origin feature/my-new-feature

# 7. Open a Pull Request on GitHub
```

---

## Code Style

This project follows:

| Tool    | Config                                  |
|---------|-----------------------------------------|
| black   | `--line-length=100` (see `pyproject.toml`) |
| flake8  | max-line-length 100, E203 ignored       |
| mypy    | `ignore_missing_imports = true`         |

Run all checks before committing:

```bash
black src/ tests/
flake8 src/ tests/ --max-line-length=100 --extend-ignore=E203
mypy src/ngs --ignore-missing-imports
```

---

## Running Tests

```bash
# All tests with coverage
pytest tests/ -v --cov=src/ngs --cov-report=term-missing

# Single test file
pytest tests/test_parse_vcf.py -v
```

---

## Pull Request Process

1. Ensure all tests pass (`pytest tests/`).
2. Ensure code passes linting (`flake8`) and formatting (`black --check`).
3. Update documentation if behaviour has changed.
4. Reference the relevant issue number in the PR description (`Closes #42`).
5. A maintainer will review and merge (or request changes).

---

Thank you for helping improve this pipeline! 🧬
