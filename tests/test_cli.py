from market_regime_classification.cli.main import build_parser


def test_cli_parser_builds() -> None:
    parser = build_parser()
    args = parser.parse_args(["--version"])
    assert args.version is True
