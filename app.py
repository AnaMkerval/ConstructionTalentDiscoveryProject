import streamlit as st

from services.gemini_service import (
    analyze_role,
    generate_search_queries
)

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
        st.warning("Please describe the role requirements first.")
    elif not location.strip():
        st.warning("Please enter a location.")
    else:
        try:
            with st.spinner("Analyzing construction role..."):
                role_requirements = analyze_role(
                role_description,
                 location
                        )

                st.success("Role analyzed successfully.")

                st.header("Structured search requirements")

                st.json(role_requirements)

                with st.spinner("Creating construction-specific search strategies..."):
                       search_queries = generate_search_queries(role_requirements)

                st.success("Search strategies created.")

                st.header("Search strategies")

                st.json(search_queries)
        except Exception as error:
            st.error("The role analysis failed.")
            st.code(str(error))