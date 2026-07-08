import os

APP_NAME = "TalentCopilot Enterprise"
APP_VERSION = "dic-v2.0-alpha-l"

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")
