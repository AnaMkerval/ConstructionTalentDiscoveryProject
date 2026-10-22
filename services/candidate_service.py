import json
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types


load_dotenv()


def extract_candidates(
    role_requirements: dict,
    web_results: list[dict]
) -> list[dict]:

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError("GEMINI_API_KEY was not found.")

    client = genai.Client(api_key=api_key)

    source_text = []

    for index, result in enumerate(web_results[:25], start=1):
        source_text.append(
            f"""
SOURCE {index}
Title: {result.get("title", "")}
URL: {result.get("url", "")}
Search query: {result.get("query", "")}

Content:
{result.get("content", "")[:2500]}
"""
        )

    sources = "\n".join(source_text)

    prompt = f"""
You are a construction recruiting research assistant.

Recruiting requirements:
{json.dumps(role_requirements, indent=2)}

Public sources:
{sources}

Identify possible real construction candidates from the sources.

Return only valid JSON using this format:

{{
  "candidates": [
    {{
      "name": "",
      "professional_identity": "",
      "location": "",
      "match_summary": "",
      "match_reasons": [],
      "concerns": [],
      "verified_facts": [
        {{
          "claim": "",
          "evidence": "",
          "source_url": ""
        }}
      ],
      "reasonable_inferences": [
        {{
          "claim": "",
          "reasoning": "",
          "source_url": ""
        }}
      ],
      "unknowns": [],
      "sources": []
    }}
  ]
}}

Important rules:

1. Include real people only.
2. Look for people in construction-related roles.
3. Accept titles such as Superintendent, General Superintendent,
   Field Superintendent, Site Manager, Construction Manager,
   Project Manager, Field Manager, and similar titles.
4. Include candidates if the source provides evidence that they work
   in construction, even if they do not exactly match every requirement.
5. Exclude school superintendents, education administrators, teachers,
   principals, recruiters, and unrelated administrators.
6. Do not include companies as candidates.
7. Do not include generic job listings as candidates unless the page
   also identifies a specific real person.
8. Do not invent candidate names or experience.
9. Every verified fact must include evidence and an exact source URL.
10. Use only URLs provided above.
11. Clearly list missing requirements under unknowns.
12. Return up to 8 possible candidates.
13. Return JSON only.
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.3,
            response_mime_type="application/json"
        )
    )

    try:
        result = json.loads(response.text)
    except json.JSONDecodeError as error:
        raise ValueError(
            f"Gemini returned invalid JSON: {response.text}"
        ) from error

    candidates = result.get("candidates", [])

    cleaned_candidates = []

    for candidate in candidates:

        if not isinstance(candidate, dict):
            continue

        name = str(
            candidate.get("name", "")
        ).strip()

        verified_facts = candidate.get(
            "verified_facts",
            []
        )

        if not name:
            continue

        if not verified_facts:
            continue

        source_urls = []

        for fact in verified_facts:
            if isinstance(fact, dict):
                source_url = str(
                    fact.get("source_url", "")
                ).strip()

                if source_url and source_url not in source_urls:
                    source_urls.append(source_url)

        for source in candidate.get("sources", []):
            source = str(source).strip()

            if source and source not in source_urls:
                source_urls.append(source)

        candidate["sources"] = source_urls

        cleaned_candidates.append(candidate)

    return cleaned_candidates[:8]