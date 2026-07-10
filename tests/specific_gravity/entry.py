from tests.specific_gravity.calculations import (
    calculate_specific_gravity
)
import streamlit as st
from utils.database import get_supabase

supabase = get_supabase()


@st.cache_data(ttl=30)
def load_sg_data(
    project_id,
    borehole_id
):

    project = (
        supabase
        .table("projects")
        .select("*")
        .eq("id", project_id)
        .single()
        .execute()
    ).data

    borehole = (
        supabase
        .table("boreholes")
        .select("*")
        .eq("id", borehole_id)
        .single()
        .execute()
    ).data

    submission = (
        supabase
        .table("specific_gravity_submissions")
        .select("*")
        .eq("project_id", project_id)
        .eq("borehole_id", borehole_id)
        .execute()
    ).data

    return (
        project,
        borehole,
        submission
    )


def render():

    # =====================================
    # VALIDATION
    # =====================================

    if "selected_project" not in st.session_state:

        st.error("No Project Selected")
        st.stop()

    if "selected_borehole" not in st.session_state:

        st.error("No Borehole Selected")
        st.stop()

    project_id = st.session_state[
        "selected_project"
    ]

    borehole_id = st.session_state[
        "selected_borehole"
    ]

    # =====================================
    # LOAD PROJECT
    # =====================================

    (
        project,
        borehole,
        submission
    ) = load_sg_data(
        project_id,
        borehole_id
    )

    if submission:

        submission_id = submission[0]["id"]

    else:

        response = (
            supabase
            .table("specific_gravity_submissions")
            .insert({

                "project_id":
                project_id,

                "borehole_id":
                borehole_id,

                "status":
                "Draft",

                "is_locked":
                False

            })
            .execute()
        )

        submission_id = (
            response.data[0]["id"]
        )

    # =====================================
    # LOAD SUBMISSION
    # =====================================

    submission_record = (
        supabase
        .table(
            "specific_gravity_submissions"
        )
        .select("*")
        .eq(
            "id",
            submission_id
        )
        .single()
        .execute()
    ).data

    # =====================================
    # HEADER
    # =====================================

    st.title(
        "Specific Gravity Test"
    )

    st.caption(
        f"Project : {project['project_name']}"
    )

    st.caption(
        f"Borehole : {borehole['bh_no']}"
    )

    if submission_record["status"] == "Draft":

        st.warning(
            "Status : Draft"
        )

    else:

        st.success(
            "Status : Submitted"
        )

    st.divider()

    # =====================================
    # SELECT SAMPLES
    # =====================================

    if submission_record["status"] == "Draft":

        st.subheader(
            "Select Samples For Specific Gravity"
        )

        borehole_samples = (
            supabase
            .table(
                "borehole_samples"
            )
            .select("*")
            .eq(
                "borehole_id",
                borehole_id
            )
            .order(
                "depth"
            )
            .execute()
        )

        with st.form(
            "sample_selection_form"
        ):

            existing_samples = (
                supabase
                .table("specific_gravity_depths")
                .select("sample_id")
                .eq("submission_id", submission_id)
                .execute()
            ).data

            existing_samples = {
                row["sample_id"]
                for row in existing_samples
            }
            selected_samples = []

            for sample in borehole_samples.data:

                if sample["sample_id"] in existing_samples:
                    continue

                checked = st.checkbox(

                    f"{sample['depth']} m - {sample['sample_type']}",

                    key=f"sg_{sample['id']}"

                )

                if checked:

                    selected_samples.append(
                        sample
                    )

        add_samples = (
            st.form_submit_button(
                "Create SG Test Entries"
            )
        )

        if add_samples:

            payload = []

            for sample in selected_samples:

                payload.append({

                    "submission_id":
                    submission_id,
                    "sample_id":
                    sample["sample_id"],

                    "depth":
                    sample["depth"],

                    "sample_type":
                    sample["sample_type"],
                    "material_type": sample.get("material_type"),
                        "rock_number":
                    sample.get("rock_number")

                })

            if payload:

                (
                    supabase
                    .table(
                        "specific_gravity_depths"
                    )
                    .insert(
                        payload
                    )
                    .execute()
                )
                st.success(
                    "Samples Added"
                )
                st.cache_data.clear()
                st.rerun()

    # =====================================
    # LOAD SG DEPTHS
    # =====================================

 # =====================================
# LOAD SG DEPTHS
# =====================================

    depths = (
        supabase
        .table(
            "specific_gravity_depths"
        )
        .select("*")
        .eq(
            "submission_id",
            submission_id
        )
        .order(
            "depth"
        )
        .execute()
    )

    all_trials = []

    if depths.data:

        all_trials = (

            supabase
            .table(
                "specific_gravity_tests"
            )
            .select(
                "depth_id"
            )
            .in_(
                "depth_id",
                [
                    d["id"]
                    for d in depths.data
                ]
            )
            .execute()

        ).data

    trial_lookup = {}

    for row in all_trials:

        trial_lookup[row["depth_id"]] = (
            trial_lookup.get(
                row["depth_id"],
                0
            ) + 1
        )
    for depth in depths.data:

        trials = (
            supabase
            .table("specific_gravity_tests")
            .select("specific_gravity")
            .eq("depth_id", depth["id"])
            .execute()
        ).data

        values = [
            t["specific_gravity"]
            for t in trials
            if t["specific_gravity"] is not None
        ]

        if values:

            avg = round(
                sum(values) / len(values),
                3
            )

            (
                supabase
                .table("specific_gravity_depths")
                .update({
                    "specific_gravity": avg
                })
                .eq("id", depth["id"])
                .execute()
            )
    st.subheader(
        "Specific Gravity Samples"
    )

    for depth_row in depths.data:

        with st.container(
            border=True
        ):

            c1, c2 = st.columns(
                [5, 1]
            )

            with c1:

                st.write(
                    f"### {depth_row.get('sample_id', '-')}"
                )

                st.caption(
                    f"Depth : {depth_row['depth']} m"
                )

                st.caption(
                    f"Sample Type : {depth_row.get('material_type', 'Soil')}"
                )

                if (
                    depth_row.get("material_type") == "Rock"
                    and depth_row.get("rock_number")
                ):

                    st.caption(
                        f"Rock No : {depth_row['rock_number']}"
                    )

                trial_count = trial_lookup.get(

                    depth_row["id"],

                    0

                )

                required_trials = (
                    1
                    if depth_row.get("material_type") == "Rock"
                    else 3
                )

                if trial_count >= required_trials:

                    st.success("Saved")

                    if depth_row.get("specific_gravity") is not None:

                        st.metric(
                            "Specific Gravity",
                            round(depth_row["specific_gravity"], 3)
                        )

                else:

                    st.warning("Pending")

            with c2:

                if st.button(
                    "Open",
                    key=f"depth_{depth_row['id']}"
                ):

                    st.session_state[
                        "selected_sg_depth"
                    ] = depth_row["id"]

                    st.session_state[
                        "selected_test_subpage"
                    ] = "sg_depth"

                    st.switch_page(
                        "pages/03_Test_Entry.py"
                    )

    # =====================================
    # FINAL SUBMIT
    # =====================================

    if (
        submission_record["status"]
        == "Draft"
        and len(depths.data) > 0
    ):

        st.divider()

        if st.button(
            "Final Submit Test",
            type="primary",
            use_container_width=True
        ):

            all_trials = (

                supabase
                .table(
                    "specific_gravity_tests"
                )
                .select("*")
                .in_(

                    "depth_id",

                    [

                        d["id"]

                        for d in depths.data

                    ]

                )
                .execute()

            ).data

            for row in all_trials:

                sg = calculate_specific_gravity(

                    row["m1"],

                    row["m2"],

                    row["m3"],

                    row["m4"]

                )
                # if sg is not None:

                #     st.metric(
                #         "Specific Gravity",
                #         round(sg, 3)
                #     )

                (
                    supabase
                    .table(
                        "specific_gravity_tests"
                    )
                    .update({

                        "specific_gravity":
                        sg,

                        "status":
                        "Submitted",

                        "locked":
                        True,

                        "approval_status":
                        "Pending"

                    })
                    .eq(
                        "id",
                        row["id"]
                    )
                    .execute()
                )
            (
                supabase
                .table(
                    "specific_gravity_submissions"
                )
                .update({

                    "status":
                    "Submitted",

                    "is_locked":
                    True,

                    "review_status":
                    "Pending",

                    "reviewer_comments":
                    None

                })
                .eq(
                    "id",
                    submission_id
                )
                .execute()
            )

            existing_review = (
                supabase
                .table("reviews")
                .select("*")
                .eq(
                    "project_id",
                    project_id
                )
                .eq(
                    "borehole_id",
                    borehole_id
                )
                .eq(
                    "test_name",
                    "Specific Gravity"
                )
                .execute()
            )

            if existing_review.data:

                (
                    supabase
                    .table("reviews")
                    .update({

                        "status":
                        "Pending",

                        "comments":
                        None

                    })
                    .eq(
                        "id",
                        existing_review.data[0]["id"]
                    )
                    .execute()
                )

            else:

                (
                    supabase
                    .table("reviews")
                    .insert({

                        "project_id":
                        project_id,

                        "borehole_id":
                        borehole_id,

                        "test_name":
                        "Specific Gravity",

                        "status":
                        "Pending"

                    })
                    .execute()
                )

            st.success(
                "Submitted For Review"
            )

            st.cache_data.clear()
            st.rerun()

        submitted_submissions = (
            supabase
            .table("specific_gravity_submissions")
            .select("*")
            .eq("project_id", project_id)
            .eq("borehole_id", borehole_id)
            .eq("status", "Submitted")
            .execute()
        ).data

    # st.write("Submitted submissions:", submitted_submissions)
    submitted = (
        supabase
        .table("specific_gravity_depths")
        .select(
            "*, specific_gravity_submissions!inner(status)"
        )
        .eq(
            "specific_gravity_submissions.status",
            "Submitted"
        )
        .eq(
            "submission_id",
            submission_id
        )
        .order("depth")
        .execute()
    ).data
    # st.write(submitted)
    if submitted:

        st.divider()
        st.subheader("Submitted Samples")

        for depth_row in submitted:

            with st.container(border=True):

                c1, c2 = st.columns([5, 1])

                with c1:

                    st.write(f"### {depth_row['sample_id']}")

                    st.caption(f"Depth : {depth_row['depth']} m")

                    st.caption(
                        f"Material : {depth_row.get('material_type', 'Soil')}"
                    )

                with c2:

                    if st.button(
                        "View",
                        key=f"submitted_{depth_row['id']}"
                    ):

                        st.session_state["selected_sg_depth"] = depth_row["id"]
                        st.session_state["selected_test_subpage"] = "sg_depth"

                        st.switch_page(
                            "pages/03_Test_Entry.py"
                        )