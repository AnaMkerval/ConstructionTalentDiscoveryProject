import streamlit as st

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

if st.button("Start candidate search", type="primary"):
    if not role_description.strip():
        st.warning("Please describe the role requirements first.")
    else:
        st.success("The search interface is working.")
        st.write("Live candidate search will be connected in the next steps.")