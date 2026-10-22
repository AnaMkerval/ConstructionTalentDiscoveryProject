import re


STOP_WORDS = {
    "and",
    "or",
    "the",
    "with",
    "for",
    "in",
    "of",
    "a",
    "an",
    "experience"
}


def normalize(value) -> str:
    if value is None:
        return ""

    text = str(value).lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def requirement_matches(
    requirement: str,
    candidate_text: str
) -> bool:

    requirement = normalize(requirement)
    candidate_text = normalize(candidate_text)

    if not requirement or not candidate_text:
        return False

    aliases = {
        "hospital construction experience": [
            "hospital",
            "healthcare",
            "medical center",
            "health care"
        ],
        "hospital construction": [
            "hospital",
            "healthcare",
            "medical center",
            "health care"
        ],
        "healthcare construction": [
            "healthcare",
            "health care",
            "hospital",
            "medical center"
        ],
        "commercial construction": [
            "commercial construction",
            "commercial projects",
            "commercial building",
            "commercial"
        ],
        "subcontractor coordination": [
            "subcontractor",
            "subcontractors",
            "trade contractor",
            "trade contractors",
            "contractor coordination"
        ],
        "reading construction documents and blueprints": [
            "blueprint",
            "blueprints",
            "construction drawings",
            "construction documents",
            "plans and specifications",
            "specifications"
        ],
        "reading construction documents": [
            "construction documents",
            "construction drawings",
            "blueprints",
            "plans and specifications",
            "specifications"
        ],
        "blueprint reading": [
            "blueprint",
            "blueprints",
            "construction drawings",
            "plans and specifications"
        ]
    }

    if requirement in aliases:
        return any(
            alias in candidate_text
            for alias in aliases[requirement]
        )

    if requirement in candidate_text:
        return True

    words = [
        word
        for word in requirement.split()
        if word not in STOP_WORDS and len(word) > 3
    ]

    if not words:
        return False

    matched_words = [
        word
        for word in words
        if word in candidate_text
    ]

    return len(matched_words) / len(words) >= 0.75


def rank_candidates(
    candidates: list[dict],
    role_requirements: dict
) -> list[dict]:

    if not isinstance(candidates, list):
        return []

    if not isinstance(role_requirements, dict):
        role_requirements = {}

    role_family = normalize(
        role_requirements.get(
            "role_family",
            ""
        )
    )

    alternative_titles = role_requirements.get(
        "alternative_titles",
        []
    )

    if not isinstance(alternative_titles, list):
        alternative_titles = []

    alternative_titles = [
        normalize(title)
        for title in alternative_titles
        if title
    ]

    possible_role_titles = [
        role_family,
        *alternative_titles
    ]

    required_experience = role_requirements.get(
        "required_experience",
        []
    )

    if not isinstance(required_experience, list):
        required_experience = []

    project_types = role_requirements.get(
        "project_types",
        []
    )

    if not isinstance(project_types, list):
        project_types = []

    location = normalize(
        role_requirements.get(
            "location",
            ""
        )
    )

    location_parts = [
        part.strip()
        for part in location.split(",")
        if len(part.strip()) > 3
    ]

    valid_candidates = []

    for candidate in candidates:

        if not isinstance(candidate, dict):
            continue

        professional_identity = normalize(
            candidate.get(
                "professional_identity",
                ""
            )
        )

        candidate_location = normalize(
            candidate.get(
                "location",
                ""
            )
        )

        verified_facts = candidate.get(
            "verified_facts",
            []
        )

        if not isinstance(verified_facts, list):
            verified_facts = []

        verified_text_parts = []

        for fact in verified_facts:
            if isinstance(fact, dict):
                verified_text_parts.append(
                    str(fact.get("claim", ""))
                )
                verified_text_parts.append(
                    str(fact.get("evidence", ""))
                )

        verified_text = normalize(
            " ".join(verified_text_parts)
        )

        candidate_text = (
            professional_identity
            + " "
            + verified_text
        )

        role_score = 0

        if any(
            title in candidate_text
            for title in possible_role_titles
            if title
        ):
            role_score = 25
        elif "superintendent" in candidate_text:
            role_score = 18
        elif (
            "construction manager" in candidate_text
            or "field manager" in candidate_text
        ):
            role_score = 12

        matched_experience = [
            requirement
            for requirement in required_experience
            if requirement_matches(
                requirement,
                verified_text
            )
        ]

        experience_score = 0

        if required_experience:
            experience_score = round(
                35
                * len(matched_experience)
                / len(required_experience)
            )

        matched_projects = [
            project
            for project in project_types
            if requirement_matches(
                project,
                verified_text
            )
        ]

        project_score = 0

        if project_types:
            project_score = round(
                20
                * len(matched_projects)
                / len(project_types)
            )

        location_score = 0

        if any(
            part in candidate_location
            or part in verified_text
            for part in location_parts
        ):
            location_score = 10

        source_urls = set()

        for fact in verified_facts:
            if isinstance(fact, dict):
                source_url = fact.get(
                    "source_url",
                    ""
                )

                if source_url:
                    source_urls.add(
                        str(source_url)
                    )

        evidence_score = min(
            10,
            len(source_urls) * 3
        )

        total_score = min(
            100,
            role_score
            + experience_score
            + project_score
            + location_score
            + evidence_score
        )

        candidate["match_score"] = total_score

        candidate["score_breakdown"] = {
            "role_match": role_score,
            "required_experience": experience_score,
            "project_type": project_score,
            "location": location_score,
            "public_evidence": evidence_score
        }

        candidate["matched_experience"] = matched_experience
        candidate["matched_projects"] = matched_projects

        valid_candidates.append(candidate)

    return sorted(
        valid_candidates,
        key=lambda candidate: candidate.get(
            "match_score",
            0
        ),
        reverse=True
    )