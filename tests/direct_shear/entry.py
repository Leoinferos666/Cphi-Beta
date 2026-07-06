import streamlit as st

from utils.database import supabase

from tests.direct_shear.calculations import (
    calculate_peak_shear_stress,
    calculate_direct_shear
)
READINGS = [
    50,100,150,200,250,300,
    350,400,450,500,550,600,
    650,700,750,800,850,900,
    950,1000,1050,1100,1150,1200
]

NORMAL_STRESSES = [0.5, 1.0, 1.5]
# DEFAULT_TRIALS = 3


def render():

    sample = st.session_state.get(
        "selected_sample"
    )
    # st.write("Selected Borehole:", st.session_state.get("selected_borehole"))
    # st.write("Sample Borehole:", sample["borehole_id"])
    # st.stop()

    if not sample:

        st.error(
            "No Sample Selected"
        )

        return

    # ------------------------
    # Back
    # ------------------------

    if st.button("⬅ Back"):

        st.session_state.pop(
            "selected_sample",
            None
        )

        st.session_state.pop(
            "selected_test_subpage",
            None
        )

        for i in range(20):

            # st.session_state.pop(f"blows_{i}", None)
            st.session_state.pop(f"can_{i}", None)
            st.session_state.pop(f"can_weight_{i}", None)
            st.session_state.pop(f"wet_{i}", None)
            st.session_state.pop(f"dry_{i}", None)

        st.session_state.pop("active_ds_submission", None)

        st.rerun()

    st.title(
        f"Direct Shear - {sample['sample_id']}"
    )

    st.write(
        f"Depth : {sample['depth']} m"
    )

    st.write(
        f"Sample Type : {sample['sample_type']}"
    )

    st.divider()
    # st.write("Selected Submission:", st.session_state.get("selected_submission"))   
    result = (
        supabase
        .table("ds_submissions")
        .select("*")
        .eq(
            "id",
            st.session_state["selected_submission"]
        )
        .limit(1)
        .execute()
    ).data
    # st.write(result)

    if not result:
        st.error("Submission not found")
        st.stop()

    submission = result[0]

        # st.write("Selected Project:", st.session_state["selected_project"])
        # st.write("Selected Borehole:", sample["borehole_id"])
        # st.write("Sample:", sample["sample_id"])
        # st.stop()
        # st.write(existing)
        # st.stop()

    #     if existing:

    #         submission = existing[0]
    #         # ==========================================
    # # RESET WIDGET STATE WHEN SUBMISSION CHANGES
    # # ==========================================

    current_submission = submission["id"]

    if st.session_state.get("active_ds_submission") != current_submission:

        st.session_state["active_ds_submission"] = current_submission

        for i in range(20):

            # st.session_state.pop(f"blows_{i}", None)
            st.session_state.pop(f"can_{i}", None)
            st.session_state.pop(f"can_weight_{i}", None)
            st.session_state.pop(f"wet_{i}", None)
            st.session_state.pop(f"dry_{i}", None)

        st.rerun()
        
    if "selected_submission" not in st.session_state:

        st.session_state.pop("selected_test_subpage", None)

        st.warning("Please select a sample first.")

        st.stop()


    # ==========================================
    # LOAD SAVED TRIALS
    # ==========================================
    saved_readings = (
        supabase
        .table("ds_trials")
        .select("*")
        .eq("submission_id", submission["id"])
        .execute()
    ).data
    reading_map = {
                        (r["normal_stress"], r["dial_reading"]): r
                        for r in saved_readings
                    }
    read_only = submission["review_status"] in [
    "Pending",
    "Approved"
]


    results = []
    
   
    water_content = st.number_input(
        "Water Content (%)",
        value=float(submission.get("water_content") or 0),
        disabled=read_only
    )

    final_wet_mass = st.number_input(
        "Final Wet Mass (g)",
        value=float(submission.get("final_wet_mass") or 0),
        disabled=read_only
    )
   

    st.divider()

    for stress in NORMAL_STRESSES:

        with st.expander(
            f"Normal Stress : {stress} kg/cm²",
            expanded=True
        ):

            st.markdown(
                "#### Ring Readings"
            )
            h1, h2, h3, h4, h5, h6 = st.columns([1,1,1,1,1,1])

            with h1:
                st.markdown("**Dial**")

            with h2:
                st.markdown("**ΔL (mm)**")

            with h3:
                st.markdown("**Area**")

            with h4:
                st.markdown("**Ring Reading**")

            with h5:
                st.markdown("**Force**")

            with h6:
                st.markdown("**Stress**")

            for dial in READINGS:

                displacement = dial / 100

                corrected_area = 36 * (1 - displacement / 60)

                c1, c2, c3, c4, c5, c6 = st.columns([1,1,1,1,1,1])

                with c1:
                    st.write(dial)

                with c2:
                    st.write(f"{displacement:.1f}")

                with c3:
                    st.write(f"{corrected_area:.2f}")

                with c4:

    

                    saved = reading_map.get(
                        (stress, dial),
                        {}
                    )

                    ring = st.number_input(
                        "",
                        value=float(saved.get("ring_reading") or 0),
                        key=f"ring_{stress}_{dial}",
                        min_value=0.0,
                        step=1.0,
                        label_visibility="collapsed",
                        disabled=read_only
                    )
                    shear_force = ring * 0.295
                    shear_stress = shear_force / corrected_area if corrected_area > 0 else 0
                with c5:
                    st.write(f"{shear_force:.3f}")

                with c6:
                    st.write(f"{shear_stress:.3f}")
          
                results.append({

                    "normal_stress": stress,

                    "dial_reading": dial,

                    "ring_reading": ring,

                    "displacement": displacement,

                    "corrected_area": corrected_area,

                    "shear_force": shear_force,

                    "shear_stress": shear_stress

                })
            st.divider()
    if not read_only:
        c1, c2 = st.columns(2)
        locked_state = False
        trial_payload = []

        for row in results:

            trial_payload.append({

                "submission_id": submission["id"],

                "normal_stress": row["normal_stress"],

                "dial_reading": row["dial_reading"],

                "ring_reading": row["ring_reading"],

                "shear_force": row["shear_force"],

                "shear_stress": row["shear_stress"],

                "approval_status": "Draft",

                "reviewer_comments": "",

                "locked": locked_state

            })
        with c1:

                if st.button(
                    "💾 Save Draft",
                    use_container_width=True,
                    key="ds_save_draft"
                ):
                    (
                        supabase
                        .table("ds_submissions")
                        .update({
                            "water_content": water_content,
                            "final_wet_mass": final_wet_mass,
                            "status": "Draft",
                            "review_status": "Draft"
                        })
                        .eq("id", submission["id"])
                        .execute()
                    )
                    locked_state = True

                    trial_payload = []

                    for row in results:

                        trial_payload.append({

                            "submission_id": submission["id"],

                            "normal_stress": row["normal_stress"],

                            "dial_reading": row["dial_reading"],

                            "ring_reading": row["ring_reading"],

                            "shear_force": row["shear_force"],

                            "shear_stress": row["shear_stress"],

                            "approval_status": "Draft",

                            "reviewer_comments": "",

                            "locked": locked_state

                        })
                    (
                        supabase
                        .table("ds_trials")
                        .upsert(
                            trial_payload,
                            on_conflict="submission_id,normal_stress,dial_reading"
                        )
                        .execute()
                    )
                    st.success("Draft Saved")
                    st.rerun()      

        with c2:

                if st.button(
                    "✅ Final Submit",
                    use_container_width=True,
                    key="ds_final_submit"
                ):
                    (
                        supabase
                        .table("ds_trials")
                        .upsert(
                            trial_payload,
                            on_conflict="submission_id,normal_stress,dial_reading"
                        )
                        .execute()
                    )
                    peak_points = []

                    for stress in NORMAL_STRESSES:

                        rows = [
                            r
                            for r in results
                            if r["normal_stress"] == stress
                        ]

                        peak = max(
                            rows,
                            key=lambda x: x["shear_stress"]
                        )

                        peak_points.append({
                            "normal_stress": stress,
                            "peak_shear_stress": peak["shear_stress"]
                        })

                    ds = calculate_direct_shear(peak_points)

                    (
                        supabase
                        .table("ds_submissions")
                        .update({
                            "water_content": water_content,
                            "final_wet_mass": final_wet_mass,
                            "cohesion": ds["cohesion"],
                            "phi": ds["phi"],
                            "status": "Submitted",
                            "review_status": "Pending"
                        })
                        .eq("id", submission["id"])
                        .execute()
                    )
                    # (
                    #     supabase
                    #     .table("ds_trials")
                    #     .update({
                    #         "locked": True
                    #     })
                    #     .eq("submission_id", submission["id"])
                    #     .execute()
                    # )
                    existing_review = (
                        supabase
                        .table("reviews")
                        .select("*")
                        .eq("project_id", submission["project_id"])
                        .eq("borehole_id", submission["borehole_id"])
                        .eq("sample_id", submission["sample_id"])
                        .eq("test_name", "Direct Shear")
                        .execute()
                    ).data
                    
                    if existing_review:

                        (
                            supabase
                            .table("reviews")
                            .update({
                                "status": "Pending"
                            })
                            .eq("id", existing_review[0]["id"])
                            .execute()
                        )

                    else:

                        (
                            supabase
                            .table("reviews")
                            .insert({
                                "project_id": submission["project_id"],
                                "borehole_id": submission["borehole_id"],
                                "sample_id": submission["sample_id"],
                                "test_name": "Direct Shear",
                                "status": "Pending"
                            })
                            .execute()
                        )
                    st.success("Direct Shear Test Submitted Successfully")
                    st.rerun()