import os

APP_NAME = "TalentCopilot Enterprise"
APP_VERSION = "blueprint-v1.0-a"

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")
