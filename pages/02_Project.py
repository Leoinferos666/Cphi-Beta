import streamlit as st
from utils.database import supabase
from utils.auth import (
    is_admin,
    load_user_profile
)
from utils.ui import apply_theme
st.set_page_config(
    page_title="...",
    layout="wide"
)
# st.write("")
# st.write("")
@st.cache_data(ttl=30)
def load_project_data(project_id):

    project = (
        supabase
        .table("projects")
        .select("*")
        .eq("id", project_id)
        .single()
        .execute()
    ).data

    boreholes = (
        supabase
        .table("boreholes")
        .select("*")
        .eq("project_id", project_id)
        .execute()
    ).data
    borehole_ids = [

        bh["id"]

        for bh in boreholes

    ]

    all_samples = (

        supabase
        .table(
            "borehole_samples"
        )
        .select("*")
        .in_(
            "borehole_id",
            borehole_ids
        )
        .order(
            "depth"
        )
        .execute()

    ).data
    sample_lookup = {}

    for sample in all_samples:

        sample_lookup.setdefault(

            sample["borehole_id"],

            []

        ).append(sample)

    project_tests = (
        supabase
        .table("project_tests")
        .select("*")
        .eq("project_id", project_id)
        .execute()
    ).data

    assignments = (
        supabase
        .table("test_assignments")
        .select("*")
        .eq("project_id", project_id)
        .execute()
    ).data

    technicians = (
        supabase
        .table("users")
        .select("*")
        .eq("role", "Technician")
        .eq("is_active", True)
        .execute()
    ).data

    return (
        project,
        boreholes,
        project_tests,
        sample_lookup,
        assignments,
        technicians
    )
 

apply_theme()
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
(
    project,
    boreholes,
    project_tests,
    sample_lookup,
    assignments,
    technicians
) = load_project_data(project_id)
st.title(project["project_name"])
st.caption(project.get("client_name", ""))
st.divider()
assignment_lookup = {

    a["test_name"]: a

    for a in assignments

}   
assignment_user_lookup = {

    (

        a["test_name"],

        a["assigned_user_id"]

    ): a

    for a in assignments

}
current_user = load_user_profile()
# =====================================
# LOAD TECHNICIANS
# =====================================

technician_lookup = {

    t["id"]: t

    for t in technicians

}
technician_name_lookup = {

    t["full_name"]: t

    for t in technicians

}
borehole_lookup = {

    bh["id"]: bh

    for bh in boreholes

}
# =====================================
# TEST SETTINGS
# =====================================


# st.write(
#     "Technicians:",
#     len(technicians.data)
# )

# st.write(
#     "Assignments:",
#     len(assignments.data)
# )
if is_admin():

    with st.expander(
        "⚙ Test Settings"
    ):

        

        for test in project_tests:

            st.subheader(
                test["test_name"]
            )
            current_assignment = assignment_lookup.get(
                test["test_name"]
            )

            tech_options = [

                t["full_name"]

                for t in technicians

            ]

            selected_tech = st.selectbox(

                "Assigned Technician",

                ["Unassigned"]
                +
                tech_options,

                index=(

                    0

                    if not current_assignment

                    else

                    next(

                        (

                            i + 1

                            for i, t in enumerate(
                                technicians
                            )

                            if t["id"]

                            ==

                            current_assignment[
                                "assigned_user_id"
                            ]

                        ),

                        0

                    )

                ),

                key=f"tech_{test['id']}"

            )

            image_req = st.selectbox(
                "Images",
                ["Optional", "Required"],
                index=0
                if test.get(
                    "image_requirement",
                    "Optional"
                ) == "Optional"
                else 1,
                key=f"img_{test['id']}"
            )

            graph_req = st.selectbox(
                "Graphs",
                ["Optional", "Required"],
                index=0
                if test.get(
                    "graph_requirement",
                    "Optional"
                ) == "Optional"
                else 1,
                key=f"graph_{test['id']}"
            )

            if st.button(
                "Save",
                key=f"save_{test['id']}"
            ):
                        (
                supabase
                .table(
                    "test_assignments"
                )
                .delete()
                .eq(
                    "project_id",
                    project_id
                )
                .eq(
                    "test_name",
                    test["test_name"]
                )
                .execute()
            )

            if selected_tech != "Unassigned":
                technician = technician_name_lookup[
                    selected_tech
                ]
                (
                    supabase
                    .table(
                        "test_assignments"
                    )
                    .insert({

                        "project_id":
                        project_id,

                        "test_name":
                        test["test_name"],

                        "assigned_user_id":
                        technician["id"]

                    })
                    .execute()
                )
                (
                    supabase
                    .table("project_tests")
                    .update({

                        "image_requirement":
                        image_req,

                        "graph_requirement":
                        graph_req

                    })
                    .eq(
                        "id",
                        test["id"]
                    )
                    .execute()
                )

                st.success(
                    "Updated"
                )
                st.cache_data.clear()
                st.rerun()

            st.divider()

# =====================================
# SELECTED BOREHOLE
# =====================================

# =====================================
# SELECTED BOREHOLE
# =====================================

selected_borehole = st.session_state.get(
    "selected_borehole"
)

selected_bh = None

if selected_borehole:

    selected_bh = borehole_lookup.get(
        selected_borehole
    )
if selected_bh:

    display_name = (

        selected_bh["bh_name"]

        if selected_bh.get("bh_name")

        else selected_bh["bh_no"]

    )

    st.success(
        f"Selected Borehole: {display_name}"
    )

st.divider()

# =====================================
# TESTS
# =====================================

st.subheader(
    "Available Tests"
)

if not project_tests:

    st.warning(
        "No Tests Assigned"
    )

else:

    cols = st.columns(3)

    for idx, test in enumerate(
        project_tests
    ):  
        if not is_admin():

            assignment = assignment_user_lookup.get(

                (

                    test["test_name"],

                    current_user["id"]

                )

            )
            if not assignment:

                continue

        with cols[idx % 3]:

            with st.container(
                border=True
            ):

                st.write(
                    f"### {test['test_name']}"
                )

                if selected_borehole:

                    if st.button(
                        "Open Test",
                        key=f"test_{test['id']}",
                        use_container_width=True
                    ):

                        st.session_state[
                            "selected_test"
                        ] = test["test_name"]

                        # if (
                        #     test["test_name"]
                        #     == "Specific Gravity"
                        # ):

                        #     st.switch_page(
                        #         "pages/03_Test_Entry.py"
                        #     )

                        # else:

                        #     st.info(
                        #         "Test page not built yet"
                        #     )
                        if test["test_name"] in [

                            "Specific Gravity",

                            "Grain Size Analysis",
                            "Liquid Limit"

                        ]:

                            st.switch_page(
                                "pages/03_Test_Entry.py"
                            )

                        else:

                            st.info(
                                "Test page not built yet"
                            )
                else:

                    st.caption(
                        "Select a borehole first"
                    )

st.divider()

# =====================================
# ADD BOREHOLE
# =====================================
st.subheader(
    "Boreholes"
)

         
## =====================================
# BOREHOLE LIST
# =====================================

from components.borehole_card import (
    render as render_borehole_card
)

for bh in boreholes:

    render_borehole_card(

    bh,

    sample_lookup.get(

        bh["id"],

        []

    )

)