from ollama import chat
from pydantic import BaseModel
from typing import List
import json

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

    print(json.dumps(output.model_dump(), indent=2))

    with open("tasks.json", "w") as f:
        json.dump(output.model_dump(), f, indent=2)

except Exception as e:
    print("Failed parsing JSON:")
    print(e)
    print(content)