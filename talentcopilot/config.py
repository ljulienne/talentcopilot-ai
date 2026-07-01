import os

APP_NAME = "TalentCopilot AI"
APP_VERSION = "0.2.0"

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")