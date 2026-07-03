import streamlit as st
from utils.database import supabase
import pandas as pd

st.title("Project Summary")

# Load projects
projects = (
    supabase
    .table("projects")
    .select("*")
    .execute()
)

if not projects.data:
    st.warning("No projects found")
    st.stop()

project_names = [
    p["project_name"]
    for p in projects.data
]

selected_project = st.selectbox(
    "Select Project",
    project_names
)

selected_project_record = next(
    p for p in projects.data
    if p["project_name"] == selected_project
)

# Get test results
results = (
    supabase
    .table("test_results")
    .select("*")
    .eq(
        "project_id",
        selected_project_record["id"]
    )
    .execute()
)

if results.data:

    df = pd.DataFrame(results.data)

    st.dataframe(
        df[
            [
                "test_name",
                "result",
                "status"
            ]
        ],
        use_container_width=True
    )

else:
    st.info("No tests found")