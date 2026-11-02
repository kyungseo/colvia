"""Prepare pinned macOS assets from the exact retained supply; no installation."""
from pathlib import Path
import argparse
import json
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--supply", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--version", required=True)
    parser.add_argument("--origin", required=True)
    parser.add_argument("--fixture-root", type=Path, help="render a separately identified offline fixture; never a published artifact")
    args = parser.parse_args()
    source = args.source.absolute()
    sys.path[:0] = [str(source / "distribution"), str(source / "src")]
    from macos import prepare
    result = prepare(source, args.supply.absolute(), args.output.absolute(), version=args.version,
                     origin=args.origin, fixture_root=args.fixture_root.absolute() if args.fixture_root else None)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
