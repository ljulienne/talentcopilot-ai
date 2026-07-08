from talentcopilot.ai_core.llm_router import LLMRouter
from talentcopilot.ai_core.models import AIRequest
from talentcopilot.services.ai_platform_status_service import AIPlatformStatusService
from talentcopilot.ui.design_system.components import enterprise_hero, insight_card, metric_grid, section_title
from talentcopilot.ui.design_system.theme import apply_enterprise_theme


def render_ai_platform():
    import streamlit as st

    apply_enterprise_theme()

    status = AIPlatformStatusService().build()

    enterprise_hero(
        "AI Platform",
        "Centralized AI infrastructure for prompts, models, structured outputs, cost tracking and observability.",
        "Release 1.2 — Real Intelligence",
    )

    metric_grid([
        ("Models", str(status.model_count), "Registry"),
        ("Prompts", str(status.prompt_count), "Versioned"),
        ("Cache", str(status.cache_size), "Entries"),
        ("Events", str(status.event_count), "Observed"),
    ])

    insight_card(
        "Platform principle",
        "The LLM extracts and structures information. The Decision Core remains responsible for hiring scores and recommendations.",
        "AI Governance",
    )

    tab_status, tab_prompts, tab_demo = st.tabs(["Status", "Prompt Registry", "Router Demo"])

    with tab_status:
        section_title("AI Platform Status")
        st.write(f"Sample call status: **{status.sample_status}**")
        st.write(f"Sample model: **{status.sample_model}**")
        st.write(f"Cost-tracked calls: **{status.cost_calls}**")

    with tab_prompts:
        router = LLMRouter()
        rows = [
            {
                "Prompt ID": prompt.prompt_id,
                "Version": prompt.version,
                "Purpose": prompt.purpose,
                "Expected Schema": prompt.expected_schema,
            }
            for prompt in router.prompts.list_prompts()
        ]
        st.dataframe(rows, use_container_width=True)

    with tab_demo:
        text = st.text_area(
            "Sample text",
            value="Alice Martin has HRIS, Project Management and Leadership experience.",
            height=120,
        )
        response = LLMRouter().run(
            AIRequest(
                task="ui_demo",
                prompt_id="candidate.extract.v1",
                input_text=text,
            )
        )
        st.json(response.structured_data)
        st.caption(f"Model: {response.model} · Prompt version: {response.prompt_version}")
