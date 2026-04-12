import market_regime_classification.evaluation.comparison as comparison
import market_regime_classification.evaluation.event_study as event_study
import market_regime_classification.evaluation.regime_stats as regime_stats


def test_evaluation_modules_import() -> None:
    assert comparison is not None
    assert event_study is not None
    assert regime_stats is not None
