import streamlit as st


def apply_next_style():
    st.markdown(
        """
        <style>
        .tc-hero {
            padding: 2rem 2.2rem;
            border-radius: 24px;
            background: linear-gradient(135deg, #111827 0%, #1f2937 62%, #374151 100%);
            color: white;
            margin-bottom: 1.5rem;
        }
        .tc-hero h1 {
            margin: 0;
            font-size: 2.35rem;
            letter-spacing: -0.04em;
        }
        .tc-hero p {
            margin-top: .75rem;
            font-size: 1.05rem;
            color: #e5e7eb;
            max-width: 860px;
        }
        .tc-pill {
            display: inline-block;
            padding: .25rem .65rem;
            border-radius: 999px;
            background: rgba(255,255,255,.12);
            color: #f9fafb;
            font-size: .78rem;
            margin-right: .35rem;
            margin-bottom: .65rem;
        }
        .tc-card {
            padding: 1.18rem 1.28rem;
            border-radius: 18px;
            border: 1px solid #e5e7eb;
            background: #ffffff;
            box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06);
            margin-bottom: 1rem;
            min-height: 145px;
        }
        .tc-card h3 {
            margin-top: 0;
            margin-bottom: .48rem;
            font-size: 1.05rem;
        }
        .tc-card p {
            color: #374151;
            margin-bottom: .45rem;
        }
        .tc-muted {
            color: #6b7280;
            font-size: .92rem;
        }
        .tc-recommendation {
            padding: 1.35rem;
            border-radius: 20px;
            background: #f9fafb;
            border: 1px solid #e5e7eb;
            margin-bottom: 1rem;
        }
        .tc-recommendation h3 {
            margin-top: 0;
        }
        .tc-diagnostic {
            padding: 1rem 1.1rem;
            border-radius: 16px;
            border: 1px solid #e5e7eb;
            background: #ffffff;
            margin-bottom: .8rem;
        }
        .tc-diagnostic strong {
            display:block;
            margin-bottom:.25rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def hero(title: str, subtitle: str, tag: str = "TalentCopilot Next"):
    st.markdown(
        f"""
        <div class="tc-hero">
            <div class="tc-pill">{tag}</div>
            <h1>{title}</h1>
            <p>{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def insight_card(title: str, body: str, footer: str | None = None):
    footer_html = f'<div class="tc-muted">{footer}</div>' if footer else ""
    st.markdown(
        f"""
        <div class="tc-card">
            <h3>{title}</h3>
            <p>{body}</p>
            {footer_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def recommendation_block(title: str, body: str):
    st.markdown(
        f"""
        <div class="tc-recommendation">
            <h3>{title}</h3>
            <p>{body}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def diagnostic_card(title: str, question: str, status: str):
    st.markdown(
        f"""
        <div class="tc-diagnostic">
            <strong>{title}</strong>
            <div>{question}</div>
            <div class="tc-muted">{status}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
