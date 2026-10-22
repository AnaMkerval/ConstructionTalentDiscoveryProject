import streamlit as st

from services.gemini_service import (
    analyze_role,
    generate_search_queries
)
from services.search_service import search_public_web
from services.candidate_service import extract_candidates
from services.ranking_service import rank_candidates


st.set_page_config(
    page_title="Bright Sky Recruiting",
    page_icon="🏗️",
    layout="wide"
)


if "candidates" not in st.session_state:
    st.session_state.candidates = []

if "feedback" not in st.session_state:
    st.session_state.feedback = {}


def candidate_key(candidate, index):
    return (
        candidate.get("name", "candidate")
        + "_"
        + str(index)
    )


def render_candidate(candidate, index, show_buttons=True):

    name = candidate.get(
        "name",
        "Unnamed candidate"
    )

    score = candidate.get(
        "match_score",
        0
    )

    feedback_key = candidate_key(
        candidate,
        index
    )

    current_feedback = st.session_state.feedback.get(
        feedback_key
    )

    with st.container(border=True):

        st.subheader(name)

        score_column, identity_column = st.columns(
            [1, 3]
        )

        with score_column:
            st.metric(
                "Match score",
                f"{score}/100"
            )

        with identity_column:
            st.write(
                candidate.get(
                    "professional_identity",
                    "Construction professional"
                )
            )

            if candidate.get("location"):
                st.caption(
                    f"Location: {candidate['location']}"
                )

        if current_feedback:
            st.caption(
                f"Recruiter decision: {current_feedback}"
            )

        st.markdown("#### Summary")

        st.write(
            candidate.get(
                "match_summary",
                "No summary available."
            )
        )

        score_explanation = candidate.get(
            "score_explanation",
            {}
        )

        if score_explanation:
            st.markdown("#### Score explanation")

            st.write(
                f"Role match: "
                f"{score_explanation.get('role_match', 0)}/25"
            )

            st.write(
                f"Required experience: "
                f"{score_explanation.get('required_experience', 0)}/35"
            )

            st.write(
                f"Project type: "
                f"{score_explanation.get('project_type', 0)}/20"
            )

            st.write(
                f"Location: "
                f"{score_explanation.get('location', 0)}/10"
            )

            st.write(
                f"Public evidence: "
                f"{score_explanation.get('public_evidence', 0)}/10"
            )

        verified_facts = candidate.get(
            "verified_facts",
            []
        )

        if verified_facts:
            st.markdown("#### Verified facts")

            for fact in verified_facts:
                st.markdown(
                    f"✓ **{fact.get('claim', '')}**"
                )

                st.write(
                    fact.get("evidence", "")
                )

                source_url = fact.get(
                    "source_url",
                    ""
                )

                if source_url:
                    st.markdown(
                        f"[Open evidence source]({source_url})"
                    )

        inferences = candidate.get(
            "reasonable_inferences",
            []
        )

        if inferences:
            st.markdown("#### Reasonable inferences")

            for inference in inferences:
                st.markdown(
                    f"~ **{inference.get('claim', '')}**"
                )

                st.write(
                    inference.get("reasoning", "")
                )

                source_url = inference.get(
                    "source_url",
                    ""
                )

                if source_url:
                    st.markdown(
                        f"[Open source]({source_url})"
                    )

        unknowns = candidate.get(
            "unknowns",
            []
        )

        if unknowns:
            st.markdown("#### Still unknown")

            for unknown in unknowns:
                st.write(f"? {unknown}")

        match_reasons = candidate.get(
            "match_reasons",
            []
        )

        if match_reasons:
            st.markdown("#### Why this candidate may match")

            for reason in match_reasons:
                st.write(f"• {reason}")

        concerns = candidate.get(
            "concerns",
            []
        )

        if concerns:
            st.markdown("#### Recruiter should verify")

            for concern in concerns:
                st.warning(concern)

        sources = candidate.get(
            "sources",
            []
        )

        if sources:
            st.markdown("#### Sources")

            for source in sources:
                st.markdown(
                    f"[Open original source]({source})"
                )

        if show_buttons:
            st.divider()

            button_one, button_two, button_three = st.columns(3)

            with button_one:
                if st.button(
                    "Save candidate",
                    key=f"save_{feedback_key}"
                ):
                    st.session_state.feedback[
                        feedback_key
                    ] = "Saved"

                    st.rerun()

            with button_two:
                if st.button(
                    "Relevant",
                    key=f"relevant_{feedback_key}"
                ):
                    st.session_state.feedback[
                        feedback_key
                    ] = "Relevant"

                    st.rerun()

            with button_three:
                if st.button(
                    "Not relevant",
                    key=f"irrelevant_{feedback_key}"
                ):
                    st.session_state.feedback[
                        feedback_key
                    ] = "Not relevant"

                    st.rerun()


@st.dialog("Saved candidates")
def show_saved_candidates():

    saved_candidates = []

    for index, candidate in enumerate(
        st.session_state.candidates
    ):
        feedback_key = candidate_key(
            candidate,
            index
        )

        if st.session_state.feedback.get(
            feedback_key
        ) == "Saved":
            saved_candidates.append(
                (index, candidate)
            )

    if not saved_candidates:
        st.info(
            "You have not saved any candidates yet."
        )
        return

    for index, candidate in saved_candidates:
        render_candidate(
            candidate,
            index,
            show_buttons=False
        )


st.title("🏗️ Bright Sky Recruiting")

st.subheader(
    "Construction Talent Discovery"
)

st.write(
    "Find construction candidates by searching beyond exact "
    "job titles and reviewing publicly available project experience."
)

saved_count = sum(
    1
    for feedback in st.session_state.feedback.values()
    if feedback == "Saved"
)

if st.button(
    f"Saved candidates ({saved_count})",
    type="secondary"
):
    show_saved_candidates()

st.divider()

st.header(
    "Describe the candidate you are looking for"
)

role_description = st.text_area(
    "Role requirements",
    placeholder=(
        "Example: I need a commercial construction "
        "superintendent in Southern California with "
        "healthcare project experience and subcontractor "
        "coordination experience."
    ),
    height=150
)

location = st.text_input(
    "Location",
    placeholder="Example: San Diego, California"
)

if st.button(
    "Find possible candidates",
    type="primary"
):

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
                "Searching public sources and analyzing candidates..."
            ):

                role_requirements = analyze_role(
                    role_description,
                    location
                )

                search_queries = generate_search_queries(
                    role_requirements
                )

                web_results = search_public_web(
                    search_queries
                )

                candidates = extract_candidates(
                    role_requirements,
                    web_results
                )

                candidates = rank_candidates(
                    candidates,
                    role_requirements
                )

            st.session_state.candidates = candidates
            st.session_state.feedback = {}

            st.success(
                f"Search complete. Found "
                f"{len(candidates)} possible candidates."
            )

        except Exception as error:

            st.error(
                "The candidate search failed."
            )

            st.code(str(error))


if st.session_state.candidates:

    st.header("Possible candidates")

    for index, candidate in enumerate(
        st.session_state.candidates
    ):
        render_candidate(
            candidate,
            index,
            show_buttons=True
        )

elif st.session_state.candidates == []:

    if "feedback" in st.session_state:
        pass