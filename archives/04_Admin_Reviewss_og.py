import streamlit as st
from utils.database import supabase

from utils.ui import apply_theme

st.set_page_config(
    page_title="...",
    layout="wide"
)

apply_theme()
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

if review_id:

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

    elif review["test_name"] == "Grain Size Analysis":

        st.subheader(
            "Grain Size Analysis"
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
            .execute()

        ).data

        st.write(
            f"Submissions Found: {len(submissions)}"
        )

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

                        import pandas as pd

                        st.dataframe(

                            pd.DataFrame(
                                sieves
                            )[

                                [

                                    "sieve_size",

                                    "retained_weight",

                                    "percent_retained",

                                    "cumulative_retained",

                                    "percent_passing"

                                ]

                            ],

                            use_container_width=True,

                            hide_index=True

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

                                key=f"gsa_approve_{submission['id']}"

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

                                key=f"gsa_return_{submission['id']}"

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
        with a2:

            if st.button(

                "Return",

                key=f"gsa_return_{submission['id']}"

            ):

                (
                    supabase
                    .table(
                        "gsa_submissions"
                    )
                    .update({

                        "review_status":
                        "Returned",

                        "reviewer_comments":
                        comment,

                        "status":
                        "Draft"

                    })
                    .eq(
                        "id",
                        submission["id"]
                    )
                    .execute()
                )

                (
                    supabase
                    .table(
                        "reviews"
                    )
                    .update({

                        "status":
                        "Pending",

                        "comments":
                        comment

                    })
                    .eq(
                        "id",
                        review["id"]
                    )
                    .execute()
                )

                st.warning(
                    "Returned To Technician"
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

