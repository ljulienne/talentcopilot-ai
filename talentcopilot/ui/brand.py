from __future__ import annotations

from html import escape
from pathlib import Path

BRAND_NAME = "TalentCopilot-AI"
BRAND_SHORT_NAME = "TalentCopilot"
BRAND_SLOGAN = "Human Intelligence. AI Amplified."
BRAND_CONCEPT = "Digital Synergy"

ASSET_DIR = Path(__file__).resolve().parent / "assets"
APP_ICON_PATH = ASSET_DIR / "talentcopilot_icon.png"


def brand_mark_svg(size: int = 44, *, include_glow: bool = True) -> str:
    """Return the configurable human + digital synergy mark as inline SVG."""
    glow = "filter='url(#tcGlow)'" if include_glow else ""
    return f"""
    <svg width="{size}" height="{size}" viewBox="0 0 64 64" role="img" aria-label="TalentCopilot-AI">
      <defs>
        <linearGradient id="tcHuman" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stop-color="#081B4B"/><stop offset="1" stop-color="#3157D8"/>
        </linearGradient>
        <linearGradient id="tcDigital" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stop-color="#00D4FF"/><stop offset="1" stop-color="#7C3AED"/>
        </linearGradient>
        <filter id="tcGlow" x="-40%" y="-40%" width="180%" height="180%">
          <feGaussianBlur stdDeviation="1.7" result="blur"/>
          <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
        </filter>
      </defs>
      <circle cx="20" cy="14" r="6" fill="url(#tcHuman)"/>
      <circle cx="46" cy="16" r="5" fill="#00CFE8"/>
      <path d="M11 48 C14 28 24 25 33 36 C39 43 43 45 54 29 C52 48 42 55 31 48 C22 42 20 39 11 48Z" fill="url(#tcHuman)"/>
      <path d="M53 49 C50 31 42 27 33 36 C27 42 24 44 14 31 C17 49 25 55 34 49 C42 44 45 41 53 49Z" fill="url(#tcDigital)" opacity=".96"/>
      <g stroke="#00D4FF" stroke-width="1.35" fill="none" stroke-linecap="round">
        <path d="M38 11V23"/><path d="M43 8V24"/><path d="M48 11V27"/><path d="M53 16V30"/>
      </g>
      <g fill="#DDFBFF">
        <circle cx="38" cy="10" r="1.7"/><circle cx="43" cy="7" r="1.7"/><circle cx="48" cy="10" r="1.7"/><circle cx="53" cy="15" r="1.7"/>
      </g>
      <circle cx="32" cy="38" r="3.3" fill="#FFFFFF" {glow}/>
      <circle cx="32" cy="38" r="1.9" fill="#00D4FF"/>
    </svg>
    """


def brand_lockup_html(*, version: str = "", compact: bool = False) -> str:
    mark_size = 42 if compact else 48
    version_html = f'<span class="tc-brand-version">{escape(version)}</span>' if version else ""
    return (
        '<div class="tc-brand-lockup">'
        f'<div class="tc-brand-mark">{brand_mark_svg(mark_size)}</div>'
        '<div class="tc-brand-copy">'
        f'<div class="tc-brand-name">{escape(BRAND_NAME)}</div>'
        f'<div class="tc-brand-slogan">{escape(BRAND_SLOGAN)}</div>'
        f'{version_html}</div></div>'
    )
