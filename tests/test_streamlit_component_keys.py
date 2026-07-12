import inspect

from talentcopilot.ui.design_system.components import (
    next_action_card,
)


def test_next_action_card_accepts_explicit_key():
    parameters = inspect.signature(
        next_action_card
    ).parameters

    assert "key" in parameters


def test_next_action_card_uses_explicit_streamlit_key():
    source = inspect.getsource(
        next_action_card
    )

    assert "key=key" in source
    assert "tc_next_action_" in source
    assert "inspect.currentframe().f_back" in source
