# Pivotal Product Tools

Modern Python 3.12 scripts for analyzing Pivotal product files.

## Quick Start

1.  **Install**:
    ```bash
    brew install python3
    python3 -m venv venv && source venv/bin/activate
    pip install -r requirements.txt
    ```

2.  **Run**:
    ```bash
    python3 weight.py --file-path path/to/product.pivotal
    ```

## Development

*   **Test**: `pytest`
*   **Lint/Format**: `ruff check --fix .` / `ruff format .`
*   **Type Check**: `mypy .`
