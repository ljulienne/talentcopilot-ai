"""Visual foundations for the TalentCopilot enterprise experience.

Presentation-only constants. Business scores, rankings and workflow state must
never depend on these values.
"""

COLORS = {
    "primary": "#4F46E5",
    "primary_strong": "#3730A3",
    "secondary": "#0EA5E9",
    "ai": "#7C3AED",
    "success": "#15803D",
    "success_soft": "#F0FDF4",
    "warning": "#B45309",
    "warning_soft": "#FFFBEB",
    "danger": "#B91C1C",
    "danger_soft": "#FEF2F2",
    "info": "#0369A1",
    "info_soft": "#F0F9FF",
    "background": "#F6F7FB",
    "surface": "#FFFFFF",
    "surface_subtle": "#F8FAFC",
    "text": "#111827",
    "muted": "#64748B",
    "border": "#E2E8F0",
    "border_strong": "#CBD5E1",
    "sidebar": "#111827",
}

RADIUS = {
    "sm": "8px",
    "md": "12px",
    "lg": "18px",
    "xl": "24px",
    "pill": "999px",
}

SHADOWS = {
    "sm": "0 1px 2px rgba(15, 23, 42, 0.05)",
    "md": "0 10px 28px rgba(15, 23, 42, 0.07)",
    "lg": "0 22px 56px rgba(15, 23, 42, 0.11)",
    "focus": "0 0 0 3px rgba(79, 70, 229, 0.18)",
}

SPACING = {
    "2xs": "0.25rem",
    "xs": "0.5rem",
    "sm": "0.75rem",
    "md": "1rem",
    "lg": "1.5rem",
    "xl": "2rem",
    "2xl": "3rem",
}

TYPOGRAPHY = {
    "font_family": "Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif",
    "display": "clamp(1.8rem, 3vw, 2.45rem)",
    "h1": "clamp(1.65rem, 2.5vw, 2.2rem)",
    "h2": "1.45rem",
    "h3": "1.08rem",
    "body": "0.96rem",
    "caption": "0.82rem",
}

SEMANTIC_STATES = {
    "complete": {"label": "Complete", "symbol": "✓", "tone": "success"},
    "current": {"label": "Current", "symbol": "●", "tone": "primary"},
    "pending": {"label": "Pending", "symbol": "○", "tone": "neutral"},
    "blocked": {"label": "Blocked", "symbol": "—", "tone": "muted"},
    "strong": {"label": "Strong", "symbol": "✓", "tone": "success"},
    "partial": {"label": "Partial", "symbol": "◐", "tone": "warning"},
    "missing": {"label": "Missing", "symbol": "!", "tone": "danger"},
    "confirmed": {"label": "Confirmed", "symbol": "✓", "tone": "success"},
    "unresolved": {"label": "Unresolved", "symbol": "!", "tone": "warning"},
}
