import os

APP_NAME = "TalentCopilot AI"
APP_VERSION = "v0.7.5"

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")
