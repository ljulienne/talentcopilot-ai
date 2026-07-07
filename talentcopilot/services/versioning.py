def get_app_name() -> str:
    try:
        from talentcopilot.config import APP_NAME
        return str(APP_NAME)
    except Exception:
        return "TalentCopilot-AI"


def get_app_version() -> str:
    try:
        from talentcopilot.config import APP_VERSION
        return str(APP_VERSION)
    except Exception:
        return "v0.7.2"


def get_version_summary() -> str:
    return f"{get_app_name()} · {get_app_version()}"
