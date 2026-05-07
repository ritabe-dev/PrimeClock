"""Command line entrypoint for PRP research helpers."""

from __future__ import annotations

import argparse

from .figures import generate_v0_figures


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="prp")
    subparsers = parser.add_subparsers(dest="command", required=True)

    figures = subparsers.add_parser("figures", help="generate v0 figures")
    figures.add_argument("--out", default="figures/v0", help="output directory")
    figures.add_argument("--n", type=int, default=100000, help="N value for generated figures")
    figures.add_argument("--bins", type=int, default=100, help="histogram bins")

    args = parser.parse_args(argv)
    if args.command == "figures":
        generate_v0_figures(args.out, n=args.n, bins=args.bins)
        return 0
    parser.error(f"unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

