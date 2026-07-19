from pathlib import Path
from talentcopilot.ui.design_system.v2.tokens import DesignTokens, TOKENS
from talentcopilot.ui.design_system.v2.components import _tone

def test_tokens_are_available():
    assert isinstance(TOKENS, DesignTokens)
    assert TOKENS.brand_900.startswith("#")
    assert TOKENS.radius_lg > TOKENS.radius_sm

def test_tone_normalization_is_safe():
    assert _tone("success") == "success"
    assert _tone("unknown") == "neutral"

def test_release_is_additive():
    root = Path("talentcopilot/ui/design_system")
    assert (root / "theme.py").exists()
    assert (root / "components.py").exists()
    assert (root / "v2" / "theme.py").exists()
    assert (root / "v2" / "components.py").exists()

def test_v2_does_not_reference_scoring_engines():
    prohibited = ("fit_intelligence_engine", "real_upload_ranking_service", "official_match_score =")
    for path in Path("talentcopilot/ui/design_system/v2").glob("*.py"):
        content = path.read_text(encoding="utf-8").lower()
        assert all(token not in content for token in prohibited)
