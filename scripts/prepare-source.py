"""Prepare a managed source tree for explicit source lifecycle use; never install."""
import argparse
import json
from pathlib import Path
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    source = args.source.absolute()
    sys.path[:0] = [str(source / "distribution"), str(source / "src")]
    from source_layout import prepare_source
    print(json.dumps(prepare_source(source, args.output.absolute()), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
