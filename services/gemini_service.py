import json
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types


load_dotenv()
def generate_search_queries(role_requirements: dict) -> dict:

    role_family = role_requirements.get(
        "role_family",
        "construction professional"
    )

    alternative_titles = role_requirements.get(
        "alternative_titles",
        []
    )

    project_types = role_requirements.get(
        "project_types",
        []
    )

    technical_skills = role_requirements.get(
        "technical_skills",
        []
    )

    location = role_requirements.get(
        "location",
        ""
    )

    title_1 = (
        alternative_titles[0]
        if len(alternative_titles) > 0
        else "Construction Superintendent"
    )

    title_2 = (
        alternative_titles[1]
        if len(alternative_titles) > 1
        else "Field Superintendent"
    )

    project_1 = (
        project_types[0]
        if len(project_types) > 0
        else "commercial construction"
    )

    project_2 = (
        project_types[1]
        if len(project_types) > 1
        else "healthcare construction"
    )

    skill_1 = (
        technical_skills[0]
        if len(technical_skills) > 0
        else "subcontractor coordination"
    )

    skill_2 = (
        technical_skills[1]
        if len(technical_skills) > 1
        else "construction documents"
    )

    return {
        "title_queries": [
            f"{title_1} {location} construction professional",
            f"{title_2} {location} commercial construction profile"
        ],

        "project_queries": [
            f"{role_family} {location} hospital construction project",
            f"{role_family} {location} healthcare construction projects"
        ],

        "skill_queries": [
            f"{role_family} {location} {skill_1}",
            f"{role_family} {location} {skill_2} blueprint reading"
        ],

        "company_queries": [
            f"general contractor {location} healthcare construction superintendent team",
            f"commercial contractor {location} hospital construction superintendent"
        ],

        "broader_queries": [
            f"senior superintendent {location} construction",
            f"construction field manager {location} healthcare projects"
        ]
    }
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