from html import escape
from typing import Iterable, Mapping, Sequence
import streamlit as st

_TONES = {"neutral","success","warning","risk","info"}

def _safe(value: object) -> str:
    return escape(str(value if value is not None else ""))

def _tone(value: str) -> str:
    value = str(value or "neutral").strip().lower()
    return value if value in _TONES else "neutral"

def status_badge(label: str, *, tone: str="neutral") -> None:
    st.markdown(f'<span class="tc2-badge tc2-{_tone(tone)}">{_safe(label)}</span>', unsafe_allow_html=True)

def confidence_badge(confidence) -> None:
    if confidence is None:
        status_badge("Confidence unavailable")
        return
    value = float(confidence)
    if 0 <= value <= 1:
        value *= 100
    tone, label = ("success","High") if value >= 80 else (("warning","Medium") if value >= 55 else ("risk","Low"))
    status_badge(f"{label} confidence · {value:.0f}%", tone=tone)

def executive_hero(title: str, *, subtitle=None, eyebrow="TalentCopilot", metadata=None) -> None:
    meta = ""
    if metadata:
        meta = '<div class="tc2-meta">' + "".join(
            f'<span class="tc2-badge tc2-neutral">{_safe(item)}</span>' for item in metadata if item
        ) + "</div>"
    subtitle_html = f'<p class="tc2-subtitle">{_safe(subtitle)}</p>' if subtitle else ""
    st.markdown(f'''<section class="tc2-hero"><div class="tc2-eyebrow">{_safe(eyebrow)}</div>
    <h1 class="tc2-title">{_safe(title)}</h1>{subtitle_html}{meta}</section>''', unsafe_allow_html=True)

def section_header(title: str, *, description=None) -> None:
    desc = f'<div class="tc2-section-description">{_safe(description)}</div>' if description else ""
    st.markdown(f'<div class="tc2-section"><div class="tc2-section-title">{_safe(title)}</div>{desc}</div>', unsafe_allow_html=True)

def metric_card(label: str, value, *, caption=None, badge=None, tone="neutral") -> None:
    cap = f'<div class="tc2-caption">{_safe(caption)}</div>' if caption else ""
    b = f'<div style="margin-top:10px"><span class="tc2-badge tc2-{_tone(tone)}">{_safe(badge)}</span></div>' if badge else ""
    st.markdown(f'<div class="tc2-card"><div class="tc2-label">{_safe(label)}</div><div class="tc2-value">{_safe(value)}</div>{cap}{b}</div>', unsafe_allow_html=True)

def metric_grid(metrics: Sequence[Mapping[str, object]], *, columns: int=4) -> None:
    if not metrics:
        return
    cols = st.columns(max(1, min(columns, len(metrics))))
    for i, metric in enumerate(metrics):
        with cols[i % len(cols)]:
            metric_card(str(metric.get("label","")), metric.get("value",""), caption=metric.get("caption"), badge=metric.get("badge"), tone=str(metric.get("tone","neutral")))

def insight_card(title: str, body: str, *, tone="info", badge=None) -> None:
    badge_html = f'<div style="margin-bottom:10px"><span class="tc2-badge tc2-{_tone(tone)}">{_safe(badge)}</span></div>' if badge else ""
    st.markdown(f'<div class="tc2-panel tc2-accent-{_tone(tone)}">{badge_html}<div class="tc2-panel-title">{_safe(title)}</div><div class="tc2-panel-body">{_safe(body)}</div></div>', unsafe_allow_html=True)

def recommendation_card(recommendation: str, *, reason=None, confidence=None, next_action=None) -> None:
    body = f"<strong>{_safe(recommendation)}</strong>"
    if reason: body += f"<br><br>{_safe(reason)}"
    if next_action: body += f"<br><br><strong>Next action:</strong> {_safe(next_action)}"
    st.markdown(f'<div class="tc2-panel tc2-accent-info"><div class="tc2-label">AI recommendation</div><div class="tc2-panel-body" style="margin-top:8px">{body}</div></div>', unsafe_allow_html=True)
    if confidence is not None: confidence_badge(confidence)

def evidence_card(evidence: Iterable[str], *, title="Evidence", empty_message="No supporting evidence is available.") -> None:
    items = [str(x).strip() for x in evidence if str(x).strip()]
    if not items:
        empty_state(title, empty_message)
        return
    rows = "".join(f"<li>✓ {_safe(x)}</li>" for x in items)
    st.markdown(f'<div class="tc2-panel"><div class="tc2-panel-title">{_safe(title)}</div><ul class="tc2-panel-body">{rows}</ul></div>', unsafe_allow_html=True)

def action_card(title: str, description: str, *, action_label=None, key=None, disabled=False) -> bool:
    st.markdown(f'<div class="tc2-panel tc2-accent-success"><div class="tc2-label">Recommended next step</div><div class="tc2-panel-title" style="margin-top:7px">{_safe(title)}</div><div class="tc2-panel-body">{_safe(description)}</div></div>', unsafe_allow_html=True)
    return bool(action_label and st.button(action_label, key=key, disabled=disabled, use_container_width=True, type="primary"))

def empty_state(title: str, description: str) -> None:
    st.markdown(f'<div class="tc2-empty"><div class="tc2-panel-title">{_safe(title)}</div><div class="tc2-panel-body">{_safe(description)}</div></div>', unsafe_allow_html=True)
