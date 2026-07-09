import streamlit as st
from utils.database import get_supabase

supabase = get_supabase()
from utils.ui import apply_theme
from utils.auth import (
    get_role,
    is_admin,
    logout,
    load_user_profile,
    get_current_user
)

st.set_page_config(
    page_title="C-Phi Dashboard",
    layout="wide"
)

apply_theme()

# =====================================
# AUTH
# =====================================

user = get_current_user()
# st.write("Session ID:", id(supabase))
# st.write("User:", user.email if user else "None")

if not user:
    st.switch_page("pages/00_Login.py")
    st.stop()

profile = load_user_profile()

st.sidebar.success(profile["full_name"])
st.sidebar.caption(profile["role"])
st.sidebar.write(f"Current Role: {get_role()}")

if is_admin():
    if st.sidebar.button("👥 Users"):
        st.switch_page("pages/05_Users.py")

if st.sidebar.button("Logout"):
    logout()
    st.switch_page("pages/00_Login.py")

# =====================================
# TESTS
# =====================================

TESTS = [
    # "Moisture Content",
    "Liquid Limit",
    "Plastic Limit",
    "Specific Gravity",
    "Grain Size Analysis",
    "Point Load Strength Index",
    # "Compaction Test",
    # "CBR",
    # "Triaxial Test",
    "Direct Shear Test",
    # "UCS",
    # "Permeability",
    "Rock Density & Porosity",
    "Unconfined Compressive Test",
    # "Chemical Analysis"
]
current_user = load_user_profile()
# =====================================
# LOAD PROJECTS
# =====================================

if is_admin():

    projects = (
        supabase
        .table("projects")
        .select("*")
        .order("created_at", desc=True)
        .execute()
    )

else:

    assignments = (
        supabase
        .table("test_assignments")
        .select("*")
        .eq(
            "assigned_user_id",
            current_user["id"]
        )
        .execute()
    )

    project_ids = list({

        row["project_id"]

        for row in assignments.data

    })

    if project_ids:

        projects = (
            supabase
            .table("projects")
            .select("*")
            .in_(
                "id",
                project_ids
            )
            .order(
                "created_at",
                desc=True
            )
            .execute()
        )

    else:

        class EmptyProjects:
            data = []

        projects = EmptyProjects()
all_boreholes = (
    supabase
    .table("boreholes")
    .select("project_id")
    .execute()
).data

borehole_lookup = {}

for bh in all_boreholes:

    pid = bh["project_id"]

    borehole_lookup[pid] = (
        borehole_lookup.get(pid, 0) + 1
    )

# =====================================
# HEADER
# =====================================

st.title("C-Phi Lab Management System")
st.caption("Geotechnical Investigation Dashboard")

if is_admin():
    if st.button("🔍 Admin Review"):
        st.switch_page("pages/04_Admin_Review.py")

st.divider()

# =====================================
# KPI
# =====================================

project_count = len(projects.data)
total_boreholes = (

    supabase

    .table("boreholes")

    .select("id", count="exact")

    .execute()

).count
c1, c2 = st.columns(2)

with c1:
    st.metric("Projects", project_count)

with c2:
    st.metric("Boreholes", total_boreholes)

st.divider()

# =====================================
# ADD PROJECT
# =====================================

if is_admin():

    with st.expander("➕ Add Project"):

        with st.form("project_form"):

            project_name = st.text_input("Project Name")
            client_name = st.text_input("Client Name")
            location = st.text_input("Location")

            num_boreholes = st.number_input(
                "Number of Boreholes",
                min_value=1,
                value=1,
                step=1
            )

            st.subheader("Applicable Tests")

            select_all = st.toggle("Select All Tests")

            if select_all:
                selected_tests = TESTS
            else:
                selected_tests = st.multiselect(
                    "Select Tests",
                    TESTS
                )

            save = st.form_submit_button(
                "Create Project"
            )

            if save:

                if not project_name:
                    st.error("Project Name Required")

                else:

                    response = (
                        supabase
                        .table("projects")
                        .insert({
                            "project_name": project_name,
                            "client_name": client_name,
                            "location": location,
                            # "num_boreholes": int(num_boreholes)
                        })
                        .execute()
                    )

                    project_id = response.data[0]["id"]

                    for test in selected_tests:

                        (
                            supabase
                            .table("project_tests")
                            .insert({
                                "project_id": project_id,
                                "test_name": test,
                                "image_requirement": "Optional",
                                "graph_requirement": "Optional"
                            })
                            .execute()
                        )

                    for i in range(
                        1,
                        int(num_boreholes) + 1
                    ):

                        (
                            supabase
                            .table("boreholes")
                            .insert({
                                "project_id": project_id,
                                "bh_no": f"BH-{i:02d}",
                                "depth": 0,
                                "gwt": 0,
                                "location": ""
                            })
                            .execute()
                        )

                    st.success(
                        "Project Created Successfully"
                    )

                    st.rerun()

# =====================================
# PROJECT LIST
# =====================================

st.subheader("Projects")

if not projects.data:
    st.info("No Projects Created Yet")

cols = st.columns(2)

for idx, project in enumerate(projects.data):

    with cols[idx % 2]:

        with st.container(border=True):

            # c1, c2 = st.columns(2)

            st.subheader(project["project_name"])

            st.caption(project.get("client_name", "-"))

            st.write(f"📍 {project.get('location', '-')}")

            borehole_count = borehole_lookup.get(
                project["id"],
                0
            )

            st.write(f"🕳 Boreholes : {borehole_count}")

            st.write("")

            c1, c2 = st.columns(2)

            with c1:

                if st.button(
                    "Open",
                    key=f"open_{project['id']}",
                    use_container_width=True
                ):

                    st.session_state["selected_project"] = project["id"]

                    st.switch_page("pages/02_Project.py")

            with c2:

                if is_admin():

                    if st.button(
                        "Delete",
                        key=f"delete_{project['id']}",
                        use_container_width=True
                    ):

                        st.session_state[
                            f"confirm_{project['id']}"
                        ] = True
        if (
            is_admin()
            and
            st.session_state.get(
                f"confirm_{project['id']}",
                False
            )
        ):

            st.warning(
                "Delete this project permanently?"
            )

            d1, d2 = st.columns(2)

            with d1:

                if st.button(
                    "Yes Delete",
                    key=f"yes_{project['id']}"
                ):

                    project_id = project["id"]

                    # -------------------------
                    # Reviews
                    # -------------------------

                    (
                        supabase
                        .table("reviews")
                        .delete()
                        .eq("project_id", project_id)
                        .execute()
                    )

                    # -------------------------
                    # Liquid Limit
                    # -------------------------

                    ll_submissions = (

                        supabase
                        .table("ll_submissions")
                        .select("id")
                        .eq("project_id", project_id)
                        .execute()

                    ).data

                    for s in ll_submissions:

                        (
                            supabase
                            .table("ll_trials")
                            .delete()
                            .eq("submission_id", s["id"])
                            .execute()
                        )

                    (
                        supabase
                        .table("ll_submissions")
                        .delete()
                        .eq("project_id", project_id)
                        .execute()
                    )

                    # -------------------------
                    # Grain Size Analysis
                    # -------------------------

                    gsa = (

                        supabase
                        .table("gsa_submissions")
                        .select("id")
                        .eq("project_id", project_id)
                        .execute()

                    ).data

                    for s in gsa:

                        (
                            supabase
                            .table("gsa_sieves")
                            .delete()
                            .eq("submission_id", s["id"])
                            .execute()
                        )

                    (
                        supabase
                        .table("gsa_submissions")
                        .delete()
                        .eq("project_id", project_id)
                        .execute()
                    )

                    # -------------------------
                    # Specific Gravity
                    # -------------------------

                    sg_submissions = (
                        supabase
                        .table("specific_gravity_submissions")
                        .select("id")
                        .eq("project_id", project_id)
                        .execute()
                    ).data

                    submission_ids = [s["id"] for s in sg_submissions]

                    depth_ids = []
                    if submission_ids:
                        depths = (
                            supabase
                            .table("specific_gravity_depths")
                            .select("id")
                            .in_("submission_id", submission_ids)
                            .execute()
                        ).data
                        depth_ids = [d["id"] for d in depths]

                    if depth_ids:
                        (
                            supabase
                            .table("specific_gravity_tests")
                            .delete()
                            .in_("depth_id", depth_ids)
                            .execute()
                        )

                    if submission_ids:
                        (
                            supabase
                            .table("specific_gravity_depths")
                            .delete()
                            .in_("submission_id", submission_ids)
                            .execute()
                        )

                    (
                        supabase
                        .table("specific_gravity_submissions")
                        .delete()
                        .eq("project_id", project_id)
                        .execute()
                    )

                    (
                        supabase
                        .table("specific_gravity_batches")
                        .delete()
                        .eq("project_id", project_id)
                        .execute()
                    )

                    # -------------------------
                    # Borehole Samples
                    # -------------------------

                    boreholes = (
                        supabase
                        .table("boreholes")
                        .select("id")
                        .eq("project_id", project_id)
                        .execute()
                    ).data

                    borehole_ids = [b["id"] for b in boreholes]

                    if borehole_ids:
                        (
                            supabase
                            .table("borehole_samples")
                            .delete()
                            .in_("borehole_id", borehole_ids)
                            .execute()
                        )

                    # -------------------------
                    # Project Tests
                    # -------------------------

                    (
                        supabase
                        .table("project_tests")
                        .delete()
                        .eq("project_id", project_id)
                        .execute()
                    )

                    # -------------------------
                    # Test Assignments
                    # -------------------------

                    (
                        supabase
                        .table("test_assignments")
                        .delete()
                        .eq("project_id", project_id)
                        .execute()
                    )

                    # -------------------------
                    # Boreholes
                    # -------------------------

                    (
                        supabase
                        .table("boreholes")
                        .delete()
                        .eq("project_id", project_id)
                        .execute()
                    )

                    # -------------------------
                    # Finally delete Project
                    # -------------------------

                    (
                        supabase
                        .table("projects")
                        .delete()
                        .eq("id", project_id)
                        .execute()
                    )
                    st.success(
                    "Project Deleted"
                )

                    st.rerun()

            with d2:

                if st.button(
                    "Cancel",
                    key=f"cancel_{project['id']}"
                ):

                    st.session_state[
                        f"confirm_{project['id']}"
                    ] = False

                    st.rerun()

    st.write("")