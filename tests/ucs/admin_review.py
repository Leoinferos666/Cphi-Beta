
import streamlit as st
from utils.database import get_supabase

supabase = get_supabase()
   
def render(review, project, borehole):

    # st.error("UCS render called")
    if review["test_name"] == "Unconfined Compressive Test":
        st.subheader("Unconfined Compressive Test")

        submissions = (
            supabase
            .table("ucs_submissions")
            .select("*")
            .eq("project_id", review["project_id"])
            .eq("borehole_id", review["borehole_id"])
            # .eq("status", "Submitted")
            .in_("review_status", ["Pending", "Approved", "Returned"])
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        ).data
        # st.write("UCS Submissions")
        # st.write(submissions)   

        if not submissions:

            st.warning("No submissions found.")

            st.stop()
        for submission in submissions:

            with st.container(border=True):
                # =====================================
    # Sample Information
    # =====================================

                specimens = (
                    supabase
                    .table("ucs_specimens")
                    .select("*")
                    .eq("submission_id", submission["id"])
                    .order("specimen_no")
                    .execute()
                ).data

                    # specimen = specimen[0] if specimen else {}

                st.subheader("Project Information")

                c1, c2, c3 = st.columns(3)

                with c1:
                    st.write(f"**Project Name:** {project['project_name']}")
                    st.write(f"**Borehole:** {borehole['bh_no']}")
                    # st.write(f"**Sample ID:** {submission['sample_id']}")

                # with c2:
                    # st.write(f"**Depth:** {sample.get('depth', '-')}")
                    # st.write(f"**Sample Type:** {sample.get('sample_type', '-')}")
                    # st.write(f"**SPT N Value:** {sample.get('spt_n_value', '-')}")

                with c2:
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
                st.subheader("UCS Results")

        #         st.subheader("Calculated Results")

        # st.write("UCS Specimens")

        # st.write(specimens)
        # with c2:
            
        
        #     trials = (

        #         supabase

        #         .table("ucs_specimens")

        #         .select("*")

        #         .eq(
        #             "submission_id",
        #             submission["id"]
        #         )

        #         .order("specimen_no")

        #         .execute()

        #     ).data
        

            st.subheader("Technician Readings")
            for specimen in specimens:

                with st.container(border=True):

                    st.subheader(f"Specimen {specimen['specimen_no']}")

                    c1, c2, c3 = st.columns(3)

                    with c1:
                        st.metric("Rock Number", specimen["rock_number"])
                        st.metric("Diameter (cm)", specimen["diameter"])
                        st.metric("Length (cm)", specimen["length"])

                    with c2:
                        st.metric(
                                    "L/D Ratio",
                                    "-" if specimen["ld_ratio"] is None else round(specimen["ld_ratio"], 2)
                                )

                        st.metric(
                            "Area (cm²)",
                            "-" if specimen["area"] is None else round(specimen["area"], 2)
                        )

                        st.metric(
                            "Volume (cm³)",
                            "-" if specimen["volume"] is None else round(specimen["volume"], 2)
                        )

                
                    with c3:
                        st.metric(
                        "Weight (g)",
                        "-" if specimen["weight"] is None else round(specimen["weight"], 2)
                    )

                    st.metric(
                        "Bulk Density",
                        "-" if specimen["bulk_density"] is None else round(specimen["bulk_density"], 3)
                    )

                    st.metric(
                        "UCS (MPa)",
                        "-" if specimen["ucs"] is None else round(specimen["ucs"], 2)
                    )   
                status = specimen.get("approval_status", "Pending")
                specimen_locked = specimen.get("locked", False)

                if status == "Approved":
                    st.success("Approved")
                elif status == "Returned":
                    st.error("Returned")
                else:
                    st.warning("Pending")

                review_comment = st.text_area(
                    "Reviewer Comment",
                    value=specimen.get("reviewer_comments", ""),
                    key=f"ucs_comment_{specimen['id']}",
                    disabled=specimen_locked
                )

                a1, a2 = st.columns(2)

                with a1:

                    if st.button(
                        "Approve Specimen",
                        key=f"ucs_approve_{specimen['id']}",
                        disabled=specimen_locked
                    ):

                        (
                            supabase
                            .table("ucs_specimens")
                            .update({
                                "approval_status": "Approved",
                                "reviewer_comments": review_comment,
                                "locked": True
                            })
                            .eq("id", specimen["id"])
                            .execute()
                        )
                        # -----------------------------------------
                        # Check if all specimens are approved
                        # -----------------------------------------

                        all_specimens = (
                            supabase
                            .table("ucs_specimens")
                            .select("approval_status")
                            .eq("submission_id", submission["id"])
                            .execute()
                        ).data

                        all_approved = all(
                            row["approval_status"] == "Approved"
                            for row in all_specimens
                        )

                        if all_approved:

                            (
                                supabase
                                .table("ucs_submissions")
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
                            f"Specimen {specimen['specimen_no']} Approved"
                        )

                        st.rerun()


                with a2:

                    if st.button(
                        "Return Specimen",
                        key=f"ucs_return_{specimen['id']}", 
                        disabled=specimen_locked
                    ):

                        (
                            supabase
                            .table("ucs_specimens")
                            .update({
                                "approval_status": "Returned",
                                "reviewer_comments": review_comment,
                                "locked": False
                            })
                            .eq("id", specimen["id"])
                            .execute()
                        )
                        (
                            supabase
                            .table("ucs_submissions")
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
                                f"Specimen {specimen['specimen_no']} Returned"
                            )

                        st.rerun()