def test_core_stable_imports():
    imports = [
        ("talentcopilot.config", "APP_NAME"),
        ("talentcopilot.ui.enterprise_navigation", "get_enterprise_navigation"),
        ("talentcopilot.ui.enterprise_shell", "render_enterprise_brand"),
        ("talentcopilot.ui.command_center", "render_command_center"),
        ("talentcopilot.services.command_center_service", "CommandCenterService"),
        ("talentcopilot.services.streamlit_session_bridge", "get_streamlit_session"),
    ]

    for module_name, attr in imports:
        module = __import__(module_name, fromlist=[attr])
        assert hasattr(module, attr), f"{module_name}.{attr}"
