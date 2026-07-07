import streamlit as st
from utils.database import get_supabase

supabase = get_supabase()
from components.attachments import (
    render as render_attachments
)
def calculate_specific_gravity(
    m1,
    m2,
    m3,
    m4
):

    try:

        return round(

            (m2 - m1)

            /

            (

                (m2 - m1)

                -

                (m3 - m4)

            ),

            3

        )

    except:

        return 0
@st.cache_data(ttl=30)
def load_depth_data(depth_id):

    depth = (
        supabase
        .table("specific_gravity_depths")
        .select("*")
        .eq("id", depth_id)
        .single()
        .execute()
    ).data

    submission = (
        supabase
        .table("specific_gravity_submissions")
        .select("*")
        .eq(
            "id",
            depth["submission_id"]
        )
        .single()
        .execute()
    ).data

    
    existing = (
        supabase
        .table(
            "specific_gravity_tests"
        )
        .select("*")
        .eq(
            "depth_id",
            depth_id
        )
        .order(
            "trial_no"
        )
        .execute()
    ).data

    return (
        depth,
        submission,
        existing
    )
def render():


    if "selected_sg_depth" not in st.session_state:

        st.error("No Depth Selected")
        st.stop()

    depth_id = st.session_state[
        "selected_sg_depth"
    ]

    project_id = st.session_state[
        "selected_project"
    ]

    borehole_id = st.session_state[
        "selected_borehole"
    ]

    # =====================================
    # LOAD DEPTH
    # =====================================
    (
    depth_record,
    submission,
    existing
) = load_depth_data(
    depth_id
)
    is_rock = (
        depth_record.get("material_type") == "Rock"
    )
    # =====================================
    # LOAD TRIALS
    # =====================================

    
    # existing = trials.data or []

    # =====================================
    # RETURNED TRIALS
    # =====================================

    returned_trials = [

        t

        for t in existing

        if t.get(
            "approval_status"
        ) == "Returned"

    ]

    # =====================================
    # PAGE HEADER
    # =====================================

    c1, c2 = st.columns([1, 5])

    with c1:

        if st.button("⬅ Back"):

            st.session_state.pop(
                "selected_test_subpage",
                None
            )

            st.session_state.pop(
                "selected_sg_depth",
                None
            )

            st.switch_page(
                "pages/03_Test_Entry.py"
            )

    with c2:

        st.title(
            f"Depth {depth_record['depth']} m"
        )

    st.divider()

    # =====================================
    # HELPER
    # =====================================
    
    def get_trial(n):

        for row in existing:

            if row["trial_no"] == n:

                return row

        return {}

    t1 = get_trial(1)
    t2 = get_trial(2)
    t3 = get_trial(3)

    # =====================================
    # REVIEW STATUS
    # =====================================

    review_status = submission.get(
        "review_status"
    )

    if returned_trials:

        st.error(
            "Returned By Reviewer"
        )

        for trial in returned_trials:

            st.warning(

                f"Trial {trial['trial_no']} : "

                f"{trial.get('reviewer_comments','')}"

            )

    if review_status == "Approved":

        st.success(
            "Approved By Reviewer"
        )

    elif review_status == "Rejected":

        st.error(
            "Rejected By Reviewer"
        )

    elif submission["status"] == "Submitted":

        st.info(
            "Pending Review"
        )

    # =====================================
    # READ ONLY MODE
    # =====================================

    if (

        submission["status"] == "Submitted"

        and

        not returned_trials

    ):

        st.info(
            "Submitted For Review"
        )

        for row in existing:

            st.write(
                f"### Trial {row['trial_no']}"
            )

            st.write(
                f"Status : {row.get('approval_status')}"
            )

            if row.get(
                "reviewer_comments"
            ):

                st.warning(
                    row["reviewer_comments"]
                )

        st.divider()

        render_attachments(

            project_id,

            borehole_id,

            "Specific Gravity",

            depth_record["depth"]

        )

        st.stop()

    t1_returned = (
        t1.get(
            "approval_status"
        ) == "Returned"
    )

    t2_returned = (
        t2.get(
            "approval_status"
        ) == "Returned"
    )

    t3_returned = (
        t3.get(
            "approval_status"
        ) == "Returned"
    )
    material_type = st.radio(
            "Material",
            ["Soil", "Rock"],
            index=1 if depth_record.get("material_type") == "Rock" else 0,
            horizontal=True,
            key=f"material_{depth_id}"
        )

    is_rock = material_type == "Rock"

    rock_number = depth_record.get("rock_number") or ""

    if is_rock:
        rock_number = st.text_input(
            "Rock Number",
            value=rock_number
        )

        st.divider()
    # =====================================
    # FORM
    # =====================================

    with st.form(
        "depth_form"
    ):
        # =====================================
# ROCK INFORMATION
# =====================================

                # =====================================
# SAMPLE TYPE
# =====================================

               
                st.subheader("Trial 1")

                t1_m1 = st.number_input(
                    "m1",
                    value=float(t1.get("m1", 0)),
                    disabled=(
                        submission["status"] == "Submitted"
                        and
                        not t1_returned
                    )
                )

                t1_m2 = st.number_input(
                    "m2",
                    value=float(t1.get("m2", 0)),
                    disabled=(
                        submission["status"] == "Submitted"
                        and
                        not t1_returned
                    )
                )

                t1_m3 = st.number_input(
                    "m3",
                    value=float(t1.get("m3", 0)),
                    disabled=(
                        submission["status"] == "Submitted"
                        and
                        not t1_returned
                    )
                )

                t1_m4 = st.number_input(
                    "m4",
                    value=float(t1.get("m4", 0)),
                    disabled=(
                        submission["status"] == "Submitted"
                        and
                        not t1_returned
                    )
                )

                st.divider()

                st.subheader("Trial 2")

                t2_m1 = st.number_input(
                    "m1 ",
                    value=float(t2.get("m1", 0)),
                    disabled=(
                        submission["status"] == "Submitted"
                        and
                        not t2_returned
                    )
                )

                t2_m2 = st.number_input(
                    "m2 ",
                    value=float(t2.get("m2", 0)),
                    disabled=(
                        submission["status"] == "Submitted"
                        and
                        not t2_returned
                    )
                )

                t2_m3 = st.number_input(
                    "m3 ",
                    value=float(t2.get("m3", 0)),
                    disabled=(
                        submission["status"] == "Submitted"
                        and
                        not t2_returned
                    )
                )

                t2_m4 = st.number_input(
                    "m4 ",
                    value=float(t2.get("m4", 0)),
                    disabled=(
                        submission["status"] == "Submitted"
                        and
                        not t2_returned
                    )
                )

                st.divider()

                st.subheader("Trial 3")

                t3_m1 = st.number_input(
                    "m1  ",
                    value=float(t3.get("m1", 0)),
                    disabled=(
                        submission["status"] == "Submitted"
                        and
                        not t3_returned
                    )
                )

                t3_m2 = st.number_input(
                    "m2  ",
                    value=float(t3.get("m2", 0)),
                    disabled=(
                        submission["status"] == "Submitted"
                        and
                        not t3_returned
                    )
                )

                t3_m3 = st.number_input(
                    "m3  ",
                    value=float(t3.get("m3", 0)),
                    disabled=(
                        submission["status"] == "Submitted"
                        and
                        not t3_returned
                    )
                )

                t3_m4 = st.number_input(
                    "m4  ",
                    value=float(t3.get("m4", 0)),
                    disabled=(
                        submission["status"] == "Submitted"
                        and
                        not t3_returned
                    )
                )

                save = st.form_submit_button(
                    "Save"
                )

                if save:

                    # (
                    #     supabase
                    #     .table(
                    #         "specific_gravity_tests"
                    #     )
                    #     .delete()
                    #     .eq(
                    #         "depth_id",
                    #         depth_id
                    #     )
                    #     .execute()
                    # )
                                (
                                    supabase
                                    .table("specific_gravity_depths")
                                    .update({

                                        "material_type": material_type,

                                        # "sample_type": sample_type,

                                        "rock_number": rock_number if is_rock else None

                                        })
                                    .eq(
                                        "id",
                                        depth_id
                                    )
                                    .execute()
                                )
                                trial_data = [

                                    (t1,1,t1_m1,t1_m2,t1_m3,t1_m4),
                                    (t2,2,t2_m1,t2_m2,t2_m3,t2_m4),
                                    (t3,3,t3_m1,t3_m2,t3_m3,t3_m4)

                                ]

                                for trial,trial_no,m1,m2,m3,m4 in trial_data:
                                    sg = calculate_specific_gravity(
                                        m1,
                                        m2,
                                        m3,
                                        m4
                                    )
                                    if (

                                        submission["status"] == "Submitted"

                                        and

                                        trial.get(
                                            "approval_status"
                                        ) != "Returned"

                                    ):

                                        continue

                                    if "id" in trial:

                                        (
                                            supabase
                                            .table(
                                                "specific_gravity_tests"
                                            )
                                            .update({

                                                "m1": m1,
                                                "m2": m2,
                                                "m3": m3,
                                                "m4": m4,
                                                "specific_gravity": sg,

                                                "approval_status":
                                                "Pending",

                                                "reviewer_comments":
                                                None

                                            })
                                            .eq(
                                                "id",
                                                trial["id"]
                                            )
                                            .execute()
                                        )

                                    else:

                                        (
                                            supabase
                                            .table(
                                                "specific_gravity_tests"
                                            )
                                            .insert({

                                                "project_id":
                                                project_id,

                                                "borehole_id":
                                                borehole_id,

                                                "depth_id":
                                                depth_id,

                                                "depth":
                                                depth_record["depth"],

                                                "trial_no":
                                                trial_no,

                                                "m1":
                                                m1,

                                                "m2":
                                                m2,

                                                "m3":
                                                m3,

                                                "m4":
                                                m4,
                                                "specific_gravity" :
                                                sg,  
                                                "status":
                                                "Draft",

                                                "locked":
                                                False,

                                                "approval_status":
                                                "Pending"

                                            })
                                            .execute()
                                        )

                                st.success(
                                    "Saved"
                                )
                                st.cache_data.clear()

                                st.session_state.pop(
                                    "selected_sg_depth",
                                    None
                                )

                                st.session_state.pop(
                                    "selected_test_subpage",
                                    None
                                )

                                st.switch_page(
                                    "pages/03_Test_Entry.py"
                                )
                st.divider()

    render_attachments(

            project_id, 

            borehole_id,

            "Specific Gravity",

            depth_record["depth"]

        )
