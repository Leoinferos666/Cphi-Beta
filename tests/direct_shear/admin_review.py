
import streamlit as st
from utils.database import supabase
import matplotlib.pyplot as plt
import numpy as np
def render(review, project, borehole):
    
    if review["test_name"] == "Direct Shear":
        st.subheader("Direct Shear")
        # st.write("Review:", review)

        submissions = (
            supabase
            .table("ds_submissions")
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
                st.subheader("Calculated Results")

                
                c1, c2 = st.columns(2)

                with c1:
                    st.metric(
                        "Cohesion (kg/cm²)",
                        f"{(submission.get('cohesion') or 0):.3f}"
                    )

                with c2:
                    st.metric(
                        "Friction Angle (°)",
                        f"{(submission.get('phi') or 0):.2f}"
                    )

                st.write(f"**Water Content:** {(submission.get('water_content') or 0):.2f} %")
                st.write(f"**Final Wet Mass:** {(submission.get('final_wet_mass') or 0):.2f} g")

                st.divider()
                readings = (
                    supabase
                    .table("ds_trials")
                    .select("*")
                    .eq("submission_id", submission["id"])
                    .order("normal_stress")
                    .order("dial_reading")
                    .execute()
                ).data      
            NORMAL_STRESSES = [0.5, 1.0, 1.5]

            for stress in NORMAL_STRESSES:

                st.subheader(f"Normal Stress = {stress} kg/cm²")

                rows = [
                    r for r in readings
                    if r["normal_stress"] == stress
                ]

                if not rows:
                    st.info("No readings found.")
                    continue

                table = []

                for row in rows:

                    table.append({

                        "Dial": row["dial_reading"],

                        "ΔL (mm)": round(row["dial_reading"] / 100, 2),

                        "Area": round(
                            36 * (1 - (row["dial_reading"] / 100) / 60),
                            2
                        ),

                        "Ring": row["ring_reading"],

                        "Force": round(row["shear_force"], 3),

                        "Stress": round(row["shear_stress"], 3)

                    })

                st.dataframe(
                    table,
                    use_container_width=True,
                    hide_index=True
                )

                st.divider()
        st.subheader("Peak Shear Stress Summary")

        peak_rows = []

        for stress in NORMAL_STRESSES:

            rows = [
                r for r in readings
                if r["normal_stress"] == stress
            ]

            if rows:

                peak = max(
                    rows,
                    key=lambda x: x["shear_stress"]
                )

                peak_rows.append({

                    "Normal Stress": stress,

                    "Peak Shear Stress": round(
                        peak["shear_stress"],
                        3
                    )

                })

        st.dataframe(
            peak_rows,
            use_container_width=True,
            hide_index=True
        )
        st.subheader("Failure Envelope")
        sigma = np.array([
        p["Normal Stress"]
        for p in peak_rows
    ])

    tau = np.array([
        p["Peak Shear Stress"]
        for p in peak_rows
    ])

    slope, intercept = np.polyfit(
        sigma,
        tau,
        1
    )
    fig, ax = plt.subplots(figsize=(6,5))

    ax.scatter(
        sigma,
        tau,
        s=70
    )

    x = np.linspace(
        0,
        max(sigma) * 1.2,
        100
    )

    y = slope * x + intercept

    ax.plot(
        x,
        y,
        linewidth=2
    )

    ax.set_xlabel("Normal Stress (kg/cm²)")
    ax.set_ylabel("Shear Stress (kg/cm²)")
    ax.set_title("Failure Envelope")

    ax.grid(True)

    st.pyplot(fig)
    st.metric(
        "Cohesion (c)",
        f"{intercept:.3f} kg/cm²"
    )

    st.metric(
        "Friction Angle (φ)",
        f"{np.degrees(np.arctan(slope)):.2f}°"
    )
    st.divider()

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
                .table("ds_submissions")
                .update({
                    "status": "Submitted",
                    "review_status": "Approved"
                })
                .eq("id", submission["id"])
                .execute()
            )

            st.success("Direct Shear Approved")

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
                    .table("ds_submissions")
                    .update({
                        "status": "Draft",
                        "review_status": "Returned"
                    })
                    .eq("id", submission["id"])
                    .execute()
                )

                (
                    supabase
                    .table("ds_trials")
                    .update({
                        "locked": False
                    })
                    .eq("submission_id", submission["id"])
                    .execute()
                )

                st.warning("Returned to Technician")

                st.session_state.pop("review_id", None)

                st.rerun()