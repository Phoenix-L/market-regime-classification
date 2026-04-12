"""CLI entrypoint for market-regime-classification."""

import argparse


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="market-regime",
        description="Research CLI for market regime classification workflows.",
    )
    parser.add_argument(
        "--version",
        action="store_true",
        help="Show CLI/bootstrap version information.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.version:
        print("market-regime-classification bootstrap CLI (phase 0/1)")
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
