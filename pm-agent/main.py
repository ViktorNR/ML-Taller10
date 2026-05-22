from ollama import chat
from pydantic import BaseModel
from typing import List
import json
import os
import re

# -----------------------------
# Output Schema
# -----------------------------

class Task(BaseModel):
    title: str
    priority: str

class Epic(BaseModel):
    epic: str
    tasks: List[Task]

class Output(BaseModel):
    epics: List[Epic]

# -----------------------------
# Load stories
# -----------------------------

with open("stories.txt", "r") as f:
    stories = f.read()

# -----------------------------
# Prompt
# -----------------------------

prompt = f"""
You are a senior Product Manager.

Convert the following user stories into:
- Epics
- A list of engineering tasks

Return ONLY valid JSON.
DO NOT use markdown.
DO NOT explain.

JSON format:
{{
  "epics": [
    {{
      "epic": "string",
      "tasks": [
        {{
          "title": "string",
          "description": "string",
          "priority": "Low|Medium|High",
          "estimate_hours": 1
        }}
      ]
    }}
  ]
}}

User Stories:
{stories}
"""

# -----------------------------
# Call Ollama
# -----------------------------

response = chat(
    model='llama3.1',
    messages=[
        {
            'role': 'user',
            'content': prompt,
            'format': 'json'
        }
    ]
)

content = response['message']['content']

# -----------------------------
# Parse JSON
# -----------------------------

try:
    data = json.loads(content)

    #epic = Epic(**data)

    output = Output(**data)

    epics_dir = "epics"
    os.makedirs(epics_dir, exist_ok=True)

    for epic in output.epics:
        safe_name = re.sub(r'[^\w\-_ ]', '', epic.epic).strip().replace(' ', '_')
        filename = f"{safe_name}.json"
        filepath = os.path.join(epics_dir, filename)
        with open(filepath, "w") as f:
            json.dump(epic.model_dump(), f, indent=2)
        print(f"Wrote {filepath}")

except Exception as e:
    print("Failed parsing JSON:")
    print(e)
    print(content)