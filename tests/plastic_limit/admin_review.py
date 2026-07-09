
import streamlit as st
from utils.database import get_supabase

supabase = get_supabase()
   
def render(review, project, borehole):
    
    if review["test_name"] == "Plastic Limit":
        st.subheader("Plastic Limit")

        submissions = (
            supabase
            .table("pl_submissions")
            .select("*")
            .eq("project_id", review["project_id"])
            .eq("borehole_id", review["borehole_id"])
            .eq("status", "Submitted")
            .execute()
        ).data

        if not submissions:

            st.warning("No Plastic Limit submissions found.")

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
                #     f"Plastic Limit : {submission['Plastic_limit']:.2f} %"
                # )

                # st.write(
                #     f"Flow Index : {submission['flow_index']:.2f}"
                # )
                st.subheader("Calculated Results")

            c1, c2 = st.columns(2)

            with c1:
                st.metric(
                    "Plastic Limit",
                    f"{submission['plastic_limit']:.2f} %"
                )

            with c2:
                
            
                trials = (

                    supabase

                    .table("pl_trials")

                    .select("*")

                    .eq(
                        "submission_id",
                        submission["id"]
                    )

                    .order("trial_no")

                    .execute()

                ).data
            

                st.subheader("Technician Readings")

        for trial in trials:

            with st.container(border=True):

                st.write(f"### Trial {trial['trial_no']}")

                c1, c2, c3 = st.columns(3)

                with c1:
                    # st.metric("Blows", trial["blows"])
                    
                    st.metric("Container No", trial["can_no"])

                with c2:
                    st.metric("Container Weight", trial["can_weight"])
                    st.metric("Wet + Container", trial["wet_soil_can"])

                with c3:
                    st.metric("Dry + Container", trial["dry_soil_can"])
                    st.metric(
                        "Water Content",
                        f"{(trial.get('water_content') or 0):.2f} %"
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
                key=f"pl_comment_{trial['id']}"
            )

            a1, a2 = st.columns(2)

            with a1:

                if st.button(
                    "Approve Trial",
                    key=f"pl_approve_{trial['id']}"
                ):

                    (
                        supabase
                        .table("pl_trials")
                        .update({
                            "approval_status": "Approved",
                            "reviewer_comments": trial_comment,
                            "locked": True
                        })
                        .eq("id", trial["id"])
                        .execute()
                    )
                    (
                        supabase
                        .table("pl_submissions")
                        .update({
                            "status": "Approved",
                            "review_status": "Approved"
                        })
                        .eq("id", submission["id"])
                        .execute()
                    )

                    (
                        supabase
                        .table("reviews")
                        .update({
                            "status": "Approved"
                        })
                        .eq("id", review["id"])
                        .execute()
                    )

                    st.success(
                        f"Trial {trial['trial_no']} Approved"
                    )

                    st.rerun()

            with a2:

                if st.button(
                    "Return Trial",
                    key=f"pl_return_{trial['id']}"
                ):

                    (
                        supabase
                        .table("pl_trials")
                        .update({
                            "approval_status": "Returned",
                            "reviewer_comments": trial_comment,
                            "locked": False
                        })
                        .eq("id", trial["id"])
                        .execute()
                    )
                    (
                        supabase
                        .table("pl_submissions")
                        .update({
                            "status": "Draft",
                            "review_status": "Returned"
                        })
                        .eq("id", submission["id"])
                        .execute()
                    )

                    (
                        supabase
                        .table("reviews")
                        .update({
                            "status": "Returned"
                        })
                        .eq("id", review["id"])
                        .execute()
                    )


                    st.warning(
                        f"Trial {trial['trial_no']} Returned"
                    )

                    st.rerun()
                    
                    