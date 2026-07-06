import streamlit as st

from utils.database import supabase

from utils.auth import (
    require_admin
)

from utils.ui import apply_theme

st.set_page_config(
    page_title="Manage Project",
    layout="wide"
)

apply_theme()

require_admin()

# =====================================
# VALIDATION
# =====================================

if "selected_project" not in st.session_state:

    st.error("No Project Selected")

    st.stop()

project_id = st.session_state["selected_project"]

# =====================================
# LOAD PROJECT
# =====================================

project = (

    supabase

    .table("projects")

    .select("*")

    .eq("id", project_id)

    .single()

    .execute()

).data

st.title("⚙ Manage Project")

st.caption(project["project_name"])

if st.button("⬅ Back"):

    st.switch_page("pages/02_Project.py")

st.divider()
st.subheader("Project Details")

with st.form("project_details_form"):

    project_name = st.text_input(
        "Project Name",
        value=project.get("project_name", "")
    )

    client_name = st.text_input(
        "Client Name",
        value=project.get("client_name", "")
    )

    location = st.text_input(
        "Location",
        value=project.get("location", "")
    )

    save = st.form_submit_button(
        "💾 Save Project Details"
    )

    if save:

        (
            supabase
            .table("projects")
            .update({

                "project_name": project_name,

                "client_name": client_name,

                "location": location

            })
            .eq("id", project_id)
            .execute()
        )

        st.success(
            "Project details updated."
        )

        st.rerun()
st.divider()

st.subheader("Borehole Management")

boreholes = (

    supabase

    .table("boreholes")

    .select("*")

    .eq("project_id", project_id)

    .order("bh_no")

    .execute()

).data
next_bh_no = 1

for bh in boreholes:

    try:

        number = int(
            bh["bh_no"]
            .replace("BH-", "")
            .replace("BH", "")
        )

        next_bh_no = max(
            next_bh_no,
            number + 1
        )

    except:

        pass
with st.expander("➕ Add Borehole"):

    with st.form("add_borehole"):

        bh_no = st.text_input(

            "BH No",

            value=f"BH-{next_bh_no:02d}"

        )

        bh_name = st.text_input("BH Name")

        depth = st.number_input(
            "Depth (m)",
            min_value=0.0,
            value=0.0
        )

        gwt = st.number_input(
            "GWT",
            min_value=0.0,
            value=0.0
        )

        location = st.text_input(
            "Location"
        )

        add = st.form_submit_button(
            "Add Borehole"
        )

        if add:

            (
                supabase
                .table("boreholes")
                .insert({

                    "project_id": project_id,

                    "bh_no": bh_no,

                    "bh_name": bh_name,

                    "depth": depth,

                    "gwt": gwt,

                    "location": location

                })
                .execute()
            )

            st.success("Borehole Added")

            st.rerun()