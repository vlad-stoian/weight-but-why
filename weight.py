import argparse
from pathlib import Path

from beeprint import pp

import pivotal_product


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--file-path", help="path to your .pivotal file", required=True)

    # Use parse_known_args to handle extra arguments passed by CI/CD (e.g. --api-key)
    # without crashing, even if we don't use them yet.
    args, unknown = parser.parse_known_args()

    if unknown:
        print(f"Ignoring unknown arguments: {unknown}")

    file_path = Path(args.file_path)
    print(f"Processing file: {file_path}")

    try:
        product = pivotal_product.parse_product(file_path)
        pp(product)
    except Exception as e:
        print(f"Error: {e}")
        exit(1)


if __name__ == "__main__":
    main()
