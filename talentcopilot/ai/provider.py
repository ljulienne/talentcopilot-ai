import json
import re
from openai import OpenAI
from talentcopilot.config import OPENAI_API_KEY, MODEL_NAME


client = OpenAI(api_key=OPENAI_API_KEY)


def clean_json_response(content):
    content = content.strip()
    content = re.sub(r"```json|```", "", content).strip()
    return json.loads(content)


def generate_json(prompt, system_message="You are a strict JSON generator."):
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )

    return clean_json_response(response.choices[0].message.content)