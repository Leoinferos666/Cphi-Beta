
import streamlit as st
from utils.database import get_supabase

supabase = get_supabase()
import matplotlib.pyplot as plt
import numpy as np
def render(review, project, borehole):
    
    if review["test_name"] == "Rock Density & Porosity":
        st.subheader("Rock Density & Porosity")
        # st.write("Review:", review)

        submissions = (
            supabase
            .table("rock_density_porosity_submissions")
            .select("*")
            .eq("project_id", review["project_id"])
            .eq("borehole_id", review["borehole_id"])
            # .eq("status", "Submitted")
            .in_("review_status", ["Pending", "Approved"])
            .execute()
        ).data

        if not submissions:

            st.warning("No direct shear submissions found.")

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
                    # .eq("borehole_id", review["borehole_id"])
                    # .single()
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
                #     f"direct shear : {submission['direct_shear']:.2f} %"
                # )

                # st.write(
                #     f"Flow Index : {submission['flow_index']:.2f}"
                # )
            # st.write("Submission ID from submission table:", submission["id"])
            # st.write("Review:", review)
            # st.subheader("Observation")
            # st.write("Submission ID:", submission["id"])
            observation = (
                supabase
                .table("rock_density_porosity_observations")
                .select("*")
                .eq("submission_id", submission["id"])
                .limit(1)
                .execute()
            ).data
            # st.write(observation)

            if not observation:
                st.warning("No observation found.")
                st.stop()

            observation = observation[0]
            st.subheader("Technician Readings")

            c1, c2, c3 = st.columns(3)

            with c1:
                st.metric("Rock Number", observation.get("rock_number", "-"))
                st.metric("M1", observation.get("m1", 0))
                st.metric("M4", observation.get("m4", 0))

            with c2:
                st.metric("M2", observation.get("m2", 0))
                st.metric("M5", observation.get("m5", 0))

            with c3:
                st.metric("M3", observation.get("m3", 0))

            st.divider()

            c1, c2 = st.columns(2)

            with c1:
                st.metric(
                    "Density",
                    f"{(observation.get('density') or 0):.3f}"
                )

            with c2:
                st.metric(
                    "Porosity (%)",
                    f"{(observation.get('porosity') or 0):.2f}"
                )

    review_comment = st.text_area(
        "Reviewer Comment",
        value=review.get("comments") or "",
        key=f"ds_review_comment_{review['id']}"
    )

    c1, c2 = st.columns(2)
    with c1:

        if st.button(
            "✅ Approve Test",
            use_container_width=True
        ):

            (
                supabase
                .table("reviews")
                .update({
                    "status": "Approved",
                    "comments": review_comment
                })
                .eq("id", review["id"])
                .execute()
            )

            (
                    supabase
                    .table("rock_density_porosity_observations")
                    .update({
                        "approval_status": "Approved",
                        "reviewer_comments": review_comment,
                        "locked": True
                    })
                    .eq("submission_id", submission["id"])
                    .execute()
                )
            st.success("Rock Density Porosity Approved")

            st.session_state.pop("review_id", None)

            st.rerun()
        with c2:

            if st.button(
                "Return",
                use_container_width=True
            ):

                (
                    supabase
                    .table("reviews")
                    .update({
                        "status": "Rejected",
                        "comments": review_comment
                    })
                    .eq("id", review["id"])
                    .execute()
                )

                (
                    supabase
                    .table("rock_density_porosity_submissions")
                    .update({
                        "status": "Draft",
                        "review_status": "Returned"
                    })
                    .eq("id", submission["id"])
                    .execute()
                )

                (
                    supabase
                    .table("rock_density_porosity_observations")
                    .update({
                        "locked": False
                    })
                    .eq("submission_id", submission["id"])
                    .execute()
                )

                st.warning("Returned to Technician")

                st.session_state.pop("review_id", None)

                st.rerun()