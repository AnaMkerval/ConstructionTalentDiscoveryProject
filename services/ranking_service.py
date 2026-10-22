def rank_candidates(
    candidates: list[dict],
    role_requirements: dict
) -> list[dict]:

    required_experience = [
        item.lower()
        for item in role_requirements.get(
            "required_experience",
            []
        )
    ]

    project_types = [
        item.lower()
        for item in role_requirements.get(
            "project_types",
            []
        )
    ]

    location = role_requirements.get(
        "location",
        ""
    ).lower()

    for candidate in candidates:
        verified_facts = candidate.get(
            "verified_facts",
            []
        )

        verified_text = " ".join(
            [
                f"{fact.get('claim', '')} "
                f"{fact.get('evidence', '')}"
                for fact in verified_facts
            ]
        ).lower()

        summary = candidate.get(
            "match_summary",
            ""
        ).lower()

        candidate_location = candidate.get(
            "location",
            ""
        ).lower()

        all_candidate_text = (
            verified_text
            + " "
            + summary
            + " "
            + candidate_location
        )

        matched_experience = [
            requirement
            for requirement in required_experience
            if any(
                word in all_candidate_text
                for word in requirement.split()
                if len(word) > 3
            )
        ]

        matched_projects = [
            project
            for project in project_types
            if any(
                word in all_candidate_text
                for word in project.split()
                if len(word) > 3
            )
        ]

        experience_score = 0

        if required_experience:
            experience_score = round(
                40
                * len(matched_experience)
                / len(required_experience)
            )

        project_score = 0

        if project_types:
            project_score = round(
                25
                * len(matched_projects)
                / len(project_types)
            )

        location_score = 15 if (
            location
            and (
                location in all_candidate_text
                or any(
                    part in all_candidate_text
                    for part in location.split(",")
                    if len(part.strip()) > 3
                )
            )
        ) else 0

        evidence_score = min(
            10,
            len(verified_facts) * 3
        )

        inference_score = min(
            10,
            len(
                candidate.get(
                    "reasonable_inferences",
                    []
                )
            ) * 2
        )

        total_score = min(
            100,
            experience_score
            + project_score
            + location_score
            + evidence_score
            + inference_score
        )

        candidate["match_score"] = total_score

        candidate["score_breakdown"] = {
            "required_experience": experience_score,
            "project_type": project_score,
            "location": location_score,
            "verified_evidence": evidence_score,
            "supporting_inferences": inference_score
        }

        candidate["matched_experience"] = matched_experience
        candidate["matched_projects"] = matched_projects

    return sorted(
        candidates,
        key=lambda candidate: candidate.get(
            "match_score",
            0
        ),
        reverse=True
    )