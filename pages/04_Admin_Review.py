import streamlit as st
from utils.database import get_supabase

supabase = get_supabase()

from utils.ui import apply_theme

from tests.gsa.report import render_gsa_report
from tests.liquid_limit.report import render_report
# from tests.plastic_limit.admin_review import render as render_pl_review   
from tests.plastic_limit.admin_review import render as render_pl_review
from tests.direct_shear.admin_review import render as render_ds_review
import pandas as pd


st.set_page_config(
    page_title="...",
    layout="wide"
)

apply_theme()


# =====================================
# Clear stale navigation state
# =====================================

if "admin_review_initialized" not in st.session_state:

    st.session_state.admin_review_initialized = True

    keys_to_remove = [
        "review_id",
        "selected_ll_sample",
        "selected_test_subpage",
        "selected_test",
        "ll_trial_count",
    ]

    for key in keys_to_remove:
        st.session_state.pop(key, None)

    st.rerun()
from utils.auth import is_admin

if not is_admin():

    st.error(
        "Access Denied"
    )

    st.stop()
# =====================================
# HEADER
# =====================================

c1, c2 = st.columns([1, 6])

with c1:

    if st.button(
        "🏠 Home",
        use_container_width=True
    ):

        st.session_state.pop(
            "review_id",
            None
        )

        st.switch_page(
            "pages/01_Dashboard.py"
        )

with c2:

    st.title(
        "Admin Review Panel"
    )

# =====================================
# LOAD REVIEWS
# =====================================

reviews = (
    supabase
    .table("reviews")
    .select("*")
    .order(
        "created_at",
        desc=True
    )
    .execute()
)

review_data = reviews.data or []

# =====================================
# KPI
# =====================================

pending_count = len([
    r for r in review_data
    if r["status"] == "Pending"
])

approved_count = len([
    r for r in review_data
    if r["status"] == "Approved"
])

rejected_count = len([
    r for r in review_data
    if r["status"] == "Rejected"
])

k1, k2, k3 = st.columns(3)

with k1:
    st.metric(
        "Pending",
        pending_count
    )

with k2:
    st.metric(
        "Approved",
        approved_count
    )

with k3:
    st.metric(
        "Rejected",
        rejected_count
    )

st.divider()

# =====================================
# REVIEW QUEUE
# =====================================

st.subheader(
    "Review Queue"
)

if not review_data:

    st.info(
        "No Reviews Found"
    )

else:

    for review in review_data:

        project = (
            supabase
            .table("projects")
            .select("*")
            .eq(
                "id",
                review["project_id"]
            )
            .execute()
        )

        project_name = "-"

        if project.data:

            project_name = (
                project.data[0]
                ["project_name"]
            )

        borehole = (
            supabase
            .table("boreholes")
            .select("*")
            .eq(
                "id",
                review["borehole_id"]
            )
            .execute()
        )

        bh_no = "-"

        if borehole.data:

            bh_no = (
                borehole.data[0]
                ["bh_no"]
            )

        with st.container(
            border=True
        ):

            c1, c2, c3, c4 = st.columns(
                [4, 2, 2, 1]
            )

            with c1:

                st.write(
                    f"### {project_name}"
                )

            with c2:

                st.write(
                    f"Borehole : {bh_no}"
                )

            with c3:

                st.write(
                    review["test_name"]
                )

                st.caption(
                    review["status"]
                )

            with c4:

                if st.button(
                    "Review",
                    key=f"review_{review['id']}"
                ):

                    st.session_state[
                        "review_id"
                    ] = review["id"]

                    st.rerun()

# =====================================
# REVIEW DETAIL
# =====================================

review_id = st.session_state.get(
    "review_id"
)
# st.write("review_id =", review_id)
# st.write(st.session_state)
# st.stop()
if not review_id:
    st.info("Select a review from the queue.")
    st.stop()

# Continue loading the selected review...

st.divider()

review_query = (
    supabase
    .table("reviews")
    .select("*")
    .eq(
        "id",
        review_id
    )
    .execute()
)

if not review_query.data:

    st.error(
        "Review Not Found"
    )

    st.stop()

review = review_query.data[0]
project = (
    supabase
    .table("projects")
    .select("*")
    .eq("id", review["project_id"])
    .execute()
).data[0]

borehole = (
    supabase
    .table("boreholes")
    .select("*")
    .eq("id", review["borehole_id"])
    .execute()
).data[0]
if st.button("⬅ Back to Review Queue"):

    keys_to_remove = [
        "review_id",
        "selected_ll_sample",
        "selected_test_subpage",
        "selected_test",
        "ll_trial_count",
    ]

    for key in keys_to_remove:
        st.session_state.pop(key, None)

    st.rerun()

st.subheader(
        f"{review['test_name']} Review"
    )

    # =====================================
    # SPECIFIC GRAVITY REVIEW
    # =====================================

if review["test_name"] == "Specific Gravity":

        submission_query = (
            supabase
            .table(
                "specific_gravity_submissions"
            )
            .select("*")
            .eq(
                "project_id",
                review["project_id"]
            )
            .eq(
                "borehole_id",
                review["borehole_id"]
            )
            .execute()
        )

        if not submission_query.data:

            st.error(
                "Submission Not Found"
            )

            st.stop()

        submission = (
            submission_query.data[0]
        )

        depths = (
            supabase
            .table(
                "specific_gravity_depths"
            )
            .select("*")
            .eq(
                "submission_id",
                submission["id"]
            )
            .order(
                "depth"
            )
            .execute()
        )

        for depth_row in depths.data:

            st.write(
                f"### Depth {depth_row['depth']} m"
            )

            trials = (
                supabase
                .table(
                    "specific_gravity_tests"
                )
                .select("*")
                .eq(
                    "depth_id",
                    depth_row["id"]
                )
                .order(
                    "trial_no"
                )
                .execute()
            )

            if trials.data:

                for trial in trials.data:

                    with st.container(
                        border=True
                    ):

                        st.write(
                            f"### Trial {trial['trial_no']}"
                        )

                        c1, c2, c3, c4, c5 = st.columns(5)

                        with c1:
                            st.metric(
                                "m1",
                                trial["m1"]
                            )

                        with c2:
                            st.metric(
                                "m2",
                                trial["m2"]
                            )

                        with c3:
                            st.metric(
                                "m3",
                                trial["m3"]
                            )

                        with c4:
                            st.metric(
                                "m4",
                                trial["m4"]
                            )

                        with c5:
                            st.metric(
                                "SG",
                                round(
                                    trial["specific_gravity"] or 0,
                                    3
                                )
                            )

                        status = trial.get(
                        "approval_status",
                        "Pending"
                    )

                    if status == "Approved":

                        st.success(
                            "Approved"
                        )

                    elif status == "Returned":

                        st.error(
                            "Returned"
                        )

                    else:

                        st.warning(
                            "Pending"
                        )

                        existing_comment = (
                            trial.get(
                                "reviewer_comments"
                            )
                            or ""
                        )

                        trial_comment = st.text_area(

                            "Reviewer Comment",

                            value=existing_comment,

                            key=f"comment_{trial['id']}"

                        )

                        a1, a2 = st.columns(2)

                        with a1:

                            if st.button(

                                "Approve Trial",

                                key=f"approve_{trial['id']}"

                            ):

                                (
                                    supabase
                                    .table(
                                        "specific_gravity_tests"
                                    )
                                    .update({

                                        "approval_status":
                                        "Approved",

                                        "reviewer_comments":
                                        trial_comment,

                                        "locked":
                                        True

                                    })
                                    .eq(
                                        "id",
                                        trial["id"]
                                    )
                                    .execute()
                                )

                                st.success(
                                    f"Trial {trial['trial_no']} Approved"
                                )

                                st.rerun()

                        with a2:

                            if st.button(

                                "Return Trial",

                                key=f"return_{trial['id']}"

                            ):

                                (
                                    supabase
                                    .table(
                                        "specific_gravity_tests"
                                    )
                                    .update({

                                        "approval_status":
                                        "Returned",

                                        "reviewer_comments":
                                        trial_comment,

                                        "status":
                                        "Draft",

                                        "locked":
                                        False

                                    })
                                    .eq(
                                        "id",
                                        trial["id"]
                                    )
                                    .execute()
                                )

                                st.warning(
                                    f"Trial {trial['trial_no']} Returned"
                                )

                                st.rerun()

    # =====================================
    # GRAIN SIZE ANALYSIS REVIEW
    # =====================================
if review["test_name"].strip().lower() == "direct shear":
    render_ds_review(review, project, borehole)
elif review["test_name"] == "Plastic Limit":
    render_pl_review(review, project, borehole)
    
elif review["test_name"] == "Grain Size Analysis":

        st.subheader(
            "Grain Size Analysis"
        )
        st.write(
    "Review Project ID:",
    review["project_id"]
)

        st.write(
            "Review Borehole ID:",
            review["borehole_id"]
        )

        submissions = (

            supabase
            .table(
                "gsa_submissions"
            )
            .select("*")
            .eq(
                "project_id",
                review["project_id"]
            )
            .eq(
                "borehole_id",
                review["borehole_id"]
            )
            .execute()

        ).data
        st.write(
            f"Total GSA Rows: {len(submissions)}"
        )
        # submissions = (

        #     supabase
        #     .table(
        #         "gsa_submissions"
        #     )
        #     .select("*")
        #     .eq(
        #         "project_id",
        #         review["project_id"]
        #     )
        #     .execute()

        # ).data

        # st.write(
        #     f"Submissions Found: {len(submissions)}"
        # )

        if not submissions:

            st.warning(
                "No GSA Submissions Found"
            )

        for submission in submissions:

                with st.container(
                    border=True
                ):

                    st.write(
                        f"### {submission['sample_id']} | Depth {submission['depth']} m"
                    )

                    c1, c2, c3 = st.columns(3)

                    with c1:

                        st.metric(
                            "Gravel %",
                            submission.get(
                                "gravel_percent"
                            ) or 0
                        )

                    with c2:

                        st.metric(
                            "Sand %",
                            submission.get(
                                "sand_percent"
                            ) or 0
                        )

                    with c3:

                        st.metric(
                            "Silt + Clay %",
                            submission.get(
                                "silt_clay_percent"
                            ) or 0
                        )

                    sieves = (

                        supabase
                        .table(
                            "gsa_sieves"
                        )
                        .select("*")
                        .eq(
                            "submission_id",
                            submission["id"]
                        )
                        .execute()

                    ).data
                    if sieves:

                        calculated = []

                        for row in sieves:

                            calculated.append({

                                "sieve_size":
                                row["sieve_size"],

                                "retained_weight":
                                row["retained_weight"],

                                "percent_retained":
                                row["percent_retained"],

                                "cumulative_retained":
                                row["cumulative_retained"],

                                "percent_passing":
                                row["percent_passing"]

                            })

                        st.subheader(
                            "Calculated Results"
                        )

                        st.dataframe(

                            pd.DataFrame(calculated),

                            use_container_width=True,

                            hide_index=True

                        )

                        render_gsa_report(
                            calculated
                        )
                        status = submission.get(
                        "review_status",
                        "Pending"
                    )

                        if status == "Approved":

                            st.success(
                                "Approved"
                            )

                        elif status == "Returned":

                            st.error(
                                "Returned"
                            )

                    else:

                        comment = st.text_area(

                            "Reviewer Comment",

                            key=f"gsa_comment_{submission['id']}"

                        )

                        a1, a2 = st.columns(2)

                        with a1:

                            if st.button(

                                "Approve",

                                key=f"gsa_approve_{submission['id']}_{submission['depth']}"

                            ):

                                (
                                    supabase
                                    .table(
                                        "gsa_submissions"
                                    )
                                    .update({

                                        "review_status":
                                        "Approved",

                                        "status":
                                        "Approved"

                                    })
                                    .eq(
                                        "id",
                                        submission["id"]
                                    )
                                    .execute()
                                )

                                st.success(
                                    "Approved"
                                )

                                st.rerun()

                        with a2:

                            if st.button(

                                "Return",

                                key=f"gsa_return_{submission['id']}_{submission['depth']}"

                            ):

                                (
                                    supabase
                                    .table(
                                        "gsa_submissions"
                                    )
                                    .update({

                                        "review_status":
                                        "Returned",

                                        "status":
                                        "Draft"

                                    })
                                    .eq(
                                        "id",
                                        submission["id"]
                                    )
                                    .execute()
                                )

                                st.warning(
                                    "Returned"
                                )

                                st.rerun() 
         
                    st.divider()

                    reviewer_comment = st.text_area(
                        "Reviewer Comments"
                    )

                    c1, c2 = st.columns(2)

        # =====================================
        # APPROVE
        # =====================================

        with c1:

            if False:
                (
                    supabase
                    .table("reviews")
                    .update({

                        "status":
                        "Approved",

                        "comments":
                        reviewer_comment

                    })
                    .eq(
                        "id",
                        review["id"]
                    )
                    .execute()
                )

                (
                    supabase
                    .table(
                        "specific_gravity_submissions"
                    )
                    .update({

                        "review_status":
                        "Approved",

                        "reviewer_comments":
                        reviewer_comment,

                        "is_locked":
                        True

                    })
                    .eq(
                        "project_id",
                        review["project_id"]
                    )
                    .eq(
                        "borehole_id",
                        review["borehole_id"]
                    )
                    .execute()
                )

                st.success(
                    "Review Approved"
                )

                st.session_state.pop(
                    "review_id",
                    None
                )

                st.rerun()

        # =====================================
        # REJECT
        # =====================================

        with c2:

            if False:

                (
                    supabase
                    .table("reviews")
                    .update({

                        "status":
                        "Rejected",

                        "comments":
                        reviewer_comment

                    })
                    .eq(
                        "id",
                        review["id"]
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
                        "Draft",

                        "is_locked":
                        False,

                        "review_status":
                        "Rejected",

                        "reviewer_comments":
                        reviewer_comment

                    })
                    .eq(
                        "project_id",
                        review["project_id"]
                    )
                    .eq(
                        "borehole_id",
                        review["borehole_id"]
                    )
                    .execute()
                )

                st.warning(
                    "Returned To Technician"
                )

                st.session_state.pop(
                    "review_id",
                    None
                )

                st.rerun()
elif review["test_name"] == "Liquid Limit":
    st.subheader("Liquid Limit")

    submissions = (
        supabase
        .table("ll_submissions")
        .select("*")
        .eq("project_id", review["project_id"])
        .eq("borehole_id", review["borehole_id"])
        .eq("status", "Submitted")
        .execute()
    ).data

    if not submissions:

        st.warning("No Liquid Limit submissions found.")

        st.stop()
    for submission in submissions:

        with st.container(border=True):
            # =====================================
# Sample Information
# =====================================

            sample = (
                supabase
                .table("borehole_samples")
                .select("*")
                .eq("sample_id", submission["sample_id"])
                .eq("borehole_id", review["borehole_id"])
                .execute()
            ).data

            sample = sample[0] if sample else {}

            st.subheader("Project Information")

            c1, c2, c3 = st.columns(3)

            with c1:
                st.write(f"**Project Name:** {project['project_name']}")
                st.write(f"**Borehole:** {borehole['bh_no']}")
                st.write(f"**Sample ID:** {submission['sample_id']}")

            with c2:
                st.write(f"**Depth:** {sample.get('depth', '-')}")
                st.write(f"**Sample Type:** {sample.get('sample_type', '-')}")
                st.write(f"**SPT N Value:** {sample.get('spt_n_value', '-')}")

            with c3:
                st.write(f"**Status:** {submission['status']}")
                # st.write(f"**Submitted:** {submission.get('submitted_at', '-')}")
                st.write(f"**Review Status:** {submission.get('review_status', '-')}")

            # st.write(
            #     f"### Sample : {submission['sample_id']}"
            # )

            # st.write(
            #     f"Liquid Limit : {submission['liquid_limit']:.2f} %"
            # )

            # st.write(
            #     f"Flow Index : {submission['flow_index']:.2f}"
            # )
            st.subheader("Calculated Results")

        c1, c2 = st.columns(2)

        with c1:
            st.metric(
                "Liquid Limit",
                f"{submission['liquid_limit']:.2f} %"
                if submission.get("liquid_limit") is not None
                else "-"
            )   

        with c2:
            st.metric(
                "Flow Index",
                round(submission["flow_index"], 2)
                if submission.get("flow_index") is not None
                else "-"
            )
            trials = (

                supabase

                .table("ll_trials")

                .select("*")

                .eq(
                    "submission_id",
                    submission["id"]
                )

                .order("trial_no")

                .execute()

            ).data
            render_report(
        trials,
        review_mode=True
    )

            st.subheader("Technician Readings")

    for trial in trials:

        with st.container(border=True):

            st.write(f"### Trial {trial['trial_no']}")

            c1, c2, c3 = st.columns(3)

            with c1:
                st.metric("Blows", trial["blows"])
                st.metric("Container No", trial["can_no"])

            with c2:
                st.metric("Container Weight", trial["can_weight"])
                st.metric("Wet + Container", trial["wet_soil_can"])

            with c3:
                st.metric("Dry + Container", trial["dry_soil_can"])
                st.metric(
                    "Water Content",
                    round(trial["water_content"], 2)
                )

        status = trial.get("approval_status", "Pending")

        if status == "Approved":
            st.success("Approved")

        elif status == "Returned":
            st.error("Returned")

        else:
            st.warning("Pending")

        existing_comment = (
            trial.get("reviewer_comments")
            or ""
        )

        trial_comment = st.text_area(
            "Reviewer Comment",
            value=existing_comment,
            key=f"ll_comment_{trial['id']}"
        )

        a1, a2 = st.columns(2)

        with a1:

            if st.button(
                "Approve Trial",
                key=f"ll_approve_{trial['id']}"
            ):

                (
                    supabase
                    .table("ll_trials")
                    .update({
                        "approval_status": "Approved",
                        "reviewer_comments": trial_comment,
                        "locked": True
                    })
                    .eq("id", trial["id"])
                    .execute()
                )

                st.success(
                    f"Trial {trial['trial_no']} Approved"
                )

                st.rerun()

        with a2:

            if st.button(
                "Return Trial",
                key=f"ll_return_{trial['id']}"
            ):

                (
                    supabase
                    .table("ll_trials")
                    .update({
                        "approval_status": "Returned",
                        "reviewer_comments": trial_comment,
                        "locked": False
                    })
                    .eq("id", trial["id"])
                    .execute()
                )

                st.warning(
                    f"Trial {trial['trial_no']} Returned"
                )

                st.rerun()
                
                