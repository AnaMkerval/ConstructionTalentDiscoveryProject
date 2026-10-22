import json
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types


load_dotenv()


def analyze_role(role_description: str, location: str) -> dict:
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError("GEMINI_API_KEY was not found.")

    client = genai.Client(api_key=api_key)

    prompt = f"""
You are a construction recruiting research assistant.

Analyze the recruiter requirements below and convert them into structured
search requirements.

Recruiter role description:
{role_description}

Location:
{location}

Return only valid JSON with exactly these fields:

{{
  "role_family": "main construction role",
  "alternative_titles": [],
  "required_experience": [],
  "preferred_experience": [],
  "project_types": [],
  "technical_skills": [],
  "certifications": [],
  "location": "{location}",
  "search_terms": []
}}

Important instructions:

1. Include alternative construction job titles.
2. Consider differences between general contractors, subcontractors,
   developers, and specialty contractors.
3. Do not invent requirements that were not stated or reasonably implied.
4. Use empty arrays when information is missing.
5. Return JSON only. Do not use Markdown or explanations.
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.2,
            response_mime_type="application/json"
        )
    )

    try:
        return json.loads(response.text)
    except json.JSONDecodeError as error:
        raise ValueError(
            f"Gemini returned invalid JSON: {response.text}"
        ) from error