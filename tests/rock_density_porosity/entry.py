import streamlit as st

from utils.database import get_supabase

supabase = get_supabase()

from tests.rock_density_porosity.calculations import (
    calculate_density,
    calculate_porosity,
)

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

        st.session_state.pop("active_rdp_submission", None)

        st.rerun()

    st.title(
        f"Rock Density & Porosity - {sample['sample_id']}"
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
        .table("rock_density_porosity_submissions")
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

    if st.session_state.get("active_rdp_submission") != current_submission:

        st.session_state["active_rdp_submission"] = current_submission

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
    # LOAD OBSERVATIONS
    # ==========================================
    observation = (
        supabase
        .table("rock_density_porosity_observations")
        .select("*")
        .eq("submission_id", submission["id"])
        .limit(1)
        .execute()
    ).data

    observation = observation[0] if observation else {}
 
    read_only = submission["review_status"] in [
    "Pending",
    "Approved"
]


    # ==========================
    # Rock Density & Porosity
    # ==========================
    # c1, c2 = st.columns(2)

    # with c1:
    #     st.text_input(
    #         "BH No",
    #         value=sample[""],
    #         disabled=True,
    #     )

    # with c2:
    #     st.text_input(
    #         "Depth (m)",
    #         value=str(sample["depth"]),
    #         disabled=True,
    #     )

    rock_number = st.text_input(
        "Rock Number",
        value=observation.get("rock_number") or "",
        disabled=read_only,
    )

    st.divider()

    m1 = st.number_input(
        "Mass of Container (M1)",
        value=float(observation.get("m1") or 0),
        min_value=0.0,
        step=0.01,
        disabled=read_only,
    )

    m2 = st.number_input(
        "Mass of Container immersed in Water (M2)",
        value=float(observation.get("m2") or 0),
        min_value=0.0,
        step=0.01,
        disabled=read_only,
    )

    m3 = st.number_input(
        "Mass of Container + Rock Sample immersed in Water (M3)",
        value=float(observation.get("m3") or 0),
        min_value=0.0,
        step=0.01,
        disabled=read_only,
    )

    m4 = st.number_input(
        "Mass of Rock after Minimum 1 Hour Soaking (M4)",
        value=float(observation.get("m4") or 0),
        min_value=0.0,
        step=0.01,
        disabled=read_only,
    )

    m5 = st.number_input(
        "Mass of Rock after Oven Dry (M5)",
        value=float(observation.get("m5") or 0),
        min_value=0.0,
        step=0.01,
        disabled=read_only,
    )

    density = calculate_density(m1, m2, m3, m4, m5)
    porosity = calculate_porosity(m1, m2, m3, m4, m5)

    st.divider()

    c1, c2 = st.columns(2)

    with c1:
        st.metric("Density", f"{density:.3f}")

    with c2:
        st.metric("Porosity (%)", f"{porosity:.2f}")
        
        if not read_only:
            c1, c2 = st.columns(2)
            
            with c1:

                    if st.button(
                        "💾 Save Draft",
                        use_container_width=True,
                        key="rdp_save_draft"
                    ):
                        (
                            supabase
                        .table("rock_density_porosity_submissions")
                            .update({
                                "status": "Draft",
                                "review_status": "Draft"
                            })
                            .eq("id", submission["id"])
                            .execute()
                        )
                        # locked_state = True

                        
                        observation_payload = {
                            "submission_id": submission["id"],

                            # "bh_no": bh_no,
                            # "depth_of_sample": depth,
                            "rock_number": rock_number,

                            "m1": m1,
                            "m2": m2,
                            "m3": m3,
                            "m4": m4,
                            "m5": m5,

                            "density": density,
                            "porosity": porosity,

                            "approval_status": "Draft",
                            "locked": False
                        }

                        (
                            supabase
                            .table("rock_density_porosity_observations")
                            .upsert(
                                observation_payload,
                                on_conflict="submission_id"
                            )
                            .execute()
                        )
                        st.success("Draft Saved")
                        st.rerun()      

            with c2:

                    if st.button(
                        "✅ Final Submit",
                        use_container_width=True,
                        key="rdp_final_submit"
                    ):
                        observation_payload = {
                            "submission_id": submission["id"],

                            # "bh_no": bh_no,
                            # "depth_of_sample": depth,
                            "rock_number": rock_number,

                            "m1": m1,
                            "m2": m2,
                            "m3": m3,
                            "m4": m4,
                            "m5": m5,

                            "density": density,
                            "porosity": porosity,

                            "approval_status": "Pending",
                            "locked": True
                        }

                        (
                            supabase
                            .table("rock_density_porosity_observations")
                            .upsert(
                            observation_payload,
                            on_conflict="submission_id"
                            )
                            .execute()
                        )

                        (
                            supabase
                            .table("rock_density_porosity_submissions")
                            .update({
                                "status": "Submitted",
                                "review_status": "Pending"
                            })
                            .eq("id", submission["id"])
                            .execute()
                        )

                        existing_review = (
                            supabase
                            .table("reviews")
                            .select("*")
                            .eq("project_id", submission["project_id"])
                            .eq("borehole_id", submission["borehole_id"])
                            .eq("sample_id", submission["sample_id"])
                            .eq("test_name", "Rock Density & Porosity")
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
                                    "test_name": "Rock Density & Porosity",
                                    "status": "Pending"
                                })
                                .execute()
                            )

                        st.success("Rock Density & Porosity submitted successfully.")
                        st.rerun()