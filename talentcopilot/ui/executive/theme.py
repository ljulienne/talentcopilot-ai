from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ExecutiveTheme:
    """Stable visual tokens shared by executive experiences."""

    primary: str = "#2563EB"
    ai: str = "#7C3AED"
    success: str = "#16A34A"
    warning: str = "#D97706"
    danger: str = "#DC2626"
    text: str = "#0F172A"
    muted: str = "#64748B"
    surface: str = "#FFFFFF"
    border: str = "#E2E8F0"
    radius: int = 18


THEME = ExecutiveTheme()


def apply_executive_theme() -> None:
    """Inject the executive component styles when Streamlit is available."""

    try:
        import streamlit as st
    except ImportError:
        return

    st.markdown(
        f"""
        <style>
        .tc-exec-card {{
            background: {THEME.surface};
            border: 1px solid {THEME.border};
            border-radius: {THEME.radius}px;
            padding: 1rem 1.05rem;
            margin-bottom: .8rem;
            box-shadow: 0 10px 28px rgba(15, 23, 42, .06);
        }}
        .tc-exec-label {{
            color: {THEME.muted};
            font-size: .76rem;
            font-weight: 800;
            letter-spacing: .055em;
            text-transform: uppercase;
        }}
        .tc-exec-value {{
            color: {THEME.text};
            font-size: 1.55rem;
            font-weight: 850;
            margin-top: .2rem;
        }}
        .tc-exec-body {{ color: {THEME.muted}; margin-top: .35rem; }}
        .tc-exec-progress {{
            background: #E2E8F0;
            border-radius: 999px;
            height: 8px;
            overflow: hidden;
            margin-top: .7rem;
        }}
        .tc-exec-progress > span {{
            display: block;
            height: 100%;
            border-radius: inherit;
        }}
        .tc-exec-badge {{
            display: inline-flex;
            align-items: center;
            padding: .2rem .55rem;
            border-radius: 999px;
            font-size: .75rem;
            font-weight: 800;
        }}
        .tc-exec-trace {{
            border-left: 2px solid {THEME.border};
            margin-left: .45rem;
            padding-left: 1rem;
        }}
        .tc-exec-trace-item {{ margin-bottom: .8rem; }}
        </style>
        """,
        unsafe_allow_html=True,
    )
