import streamlit as st

from services.candidate_service import extract_candidates
from services.gemini_service import (
    analyze_role,
    generate_search_queries
)
from services.search_service import search_public_web
from services.ranking_service import rank_candidates


st.set_page_config(
    page_title="Bright Sky Recruiting",
    page_icon="🏗️",
    layout="wide"
)


st.title("🏗️ Bright Sky Recruiting")
st.subheader("Construction Talent Discovery")

st.write(
    "Find construction candidates by searching beyond exact job titles "
    "and reviewing publicly available project experience."
)

st.divider()

st.header("Describe the candidate you are looking for")

role_description = st.text_area(
    "Role requirements",
    placeholder=(
        "Example: I need a commercial construction superintendent in "
        "Southern California with healthcare project experience and "
        "subcontractor coordination experience."
    ),
    height=160
)

location = st.text_input(
    "Location",
    placeholder="Example: San Diego, California"
)


if st.button("Analyze role", type="primary"):

    if not role_description.strip():
        st.warning(
            "Please describe the role requirements first."
        )

    elif not location.strip():
        st.warning(
            "Please enter a location."
        )

    else:
        try:
            with st.spinner(
                "Analyzing construction role..."
            ):
                role_requirements = analyze_role(
                    role_description,
                    location
                )

            st.success(
                "Role analyzed successfully."
            )

            st.header(
                "Structured search requirements"
            )

            st.json(
                role_requirements
            )

            with st.spinner(
                "Creating construction-specific search strategies..."
            ):
                search_queries = generate_search_queries(
                    role_requirements
                )

            st.success(
                "Search strategies created."
            )

            st.header(
                "Search strategies"
            )

            st.json(
                search_queries
            )

            with st.spinner(
                "Searching public web sources..."
            ):
                web_results = search_public_web(
                    search_queries
                )

            st.success(
                f"Found {len(web_results)} unique public web sources."
            )

            st.header(
                "Public web results"
            )

            for index, result in enumerate(
                web_results,
                start=1
            ):
                with st.expander(
                    f"{index}. {result['title']}"
                ):
                    st.caption(
                        f"Search category: "
                        f"{result['category']}"
                    )

                    st.write(
                        f"Search query: "
                        f"{result['query']}"
                    )

                    st.write(
                        result["content"]
                    )

                    st.markdown(
                        f"[Open original source]({result['url']})"
                    )

            with st.spinner(
                "Identifying possible construction candidates..."
            ):
                candidates = extract_candidates(
                    role_requirements,
                    web_results
                )

                candidates = rank_candidates(
                    candidates,
                    role_requirements
                )

            st.success(
                f"Identified {len(candidates)} possible candidates."
            )

            st.header(
                "Possible candidates"
            )

            if not candidates:
                st.info(
                    "No clearly identifiable candidates were found "
                    "in the available public sources."
                )

            for candidate in candidates:

                with st.container(border=True):

                    st.subheader(
                        candidate.get(
                            "name",
                            "Unnamed candidate"
                        )
                    )

                    st.metric(
                        "Transparent match score",
                        f"{candidate.get('match_score', 0)}/100"
                    )

                    st.write(
                        candidate.get(
                            "professional_identity",
                            "Professional identity not available."
                        )
                    )

                    if candidate.get("location"):
                        st.caption(
                            f"Location: "
                            f"{candidate['location']}"
                        )

                    st.markdown(
                        "### Summary"
                    )

                    st.write(
                        candidate.get(
                            "match_summary",
                            "No summary available."
                        )
                    )

                    st.markdown(
                        "### Score explanation"
                    )

                    score_breakdown = candidate.get(
                        "score_breakdown",
                        {}
                    )

                    st.write(
                        "Required experience: "
                        f"{score_breakdown.get('required_experience', 0)}/40"
                    )

                    st.write(
                        "Project type: "
                        f"{score_breakdown.get('project_type', 0)}/25"
                    )

                    st.write(
                        "Location: "
                        f"{score_breakdown.get('location', 0)}/15"
                    )

                    st.write(
                        "Verified evidence: "
                        f"{score_breakdown.get('verified_evidence', 0)}/10"
                    )

                    st.write(
                        "Supporting inferences: "
                        f"{score_breakdown.get('supporting_inferences', 0)}/10"
                    )

                    st.markdown(
                        "### Verified facts"
                    )

                    verified_facts = candidate.get(
                        "verified_facts",
                        []
                    )

                    if verified_facts:
                        for fact in verified_facts:

                            st.markdown(
                                f"✓ **{fact.get('claim', '')}**"
                            )

                            st.write(
                                "Evidence: "
                                f"{fact.get('evidence', '')}"
                            )

                            st.markdown(
                                f"[Source]("
                                f"{fact.get('source_url', '#')})"
                            )
                    else:
                        st.write(
                            "No verified facts were found."
                        )

                    st.markdown(
                        "### Reasonable inferences"
                    )

                    inferences = candidate.get(
                        "reasonable_inferences",
                        []
                    )

                    if inferences:
                        for inference in inferences:

                            st.markdown(
                                f"~ **{inference.get('claim', '')}**"
                            )

                            st.write(
                                "Reasoning: "
                                f"{inference.get('reasoning', '')}"
                            )

                            st.markdown(
                                f"[Source]("
                                f"{inference.get('source_url', '#')})"
                            )
                    else:
                        st.write(
                            "No reasonable inferences were identified."
                        )

                    st.markdown(
                        "### Unknowns"
                    )

                    unknowns = candidate.get(
                        "unknowns",
                        []
                    )

                    if unknowns:
                        for unknown in unknowns:
                            st.markdown(
                                f"? {unknown}"
                            )
                    else:
                        st.write(
                            "No additional unknowns were listed."
                        )

                    st.markdown(
                        "### Why this candidate may match"
                    )

                    match_reasons = candidate.get(
                        "match_reasons",
                        []
                    )

                    if match_reasons:
                        for reason in match_reasons:
                            st.markdown(
                                f"- {reason}"
                            )
                    else:
                        st.write(
                            "No specific match reasons were identified."
                        )

                    st.markdown(
                        "### Sources"
                    )

                    sources = candidate.get(
                        "sources",
                        []
                    )

                    if sources:
                        for source in sources:
                            st.markdown(
                                f"- [Open source]({source})"
                            )
                    else:
                        st.write(
                            "No source links were returned."
                        )

        except Exception as error:
            st.error(
                "The role analysis, web search, or candidate "
                "extraction failed."
            )

            st.code(
                str(error)
            )