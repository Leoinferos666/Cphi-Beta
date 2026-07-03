import streamlit as st

from utils.database import supabase

from tests.liquid_limit.calculations import (
    calculate_water_content,
    calculate_liquid_limit
)

DEFAULT_TRIALS = 3


def render():

    sample = st.session_state.get(
        "selected_ll_sample"
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
            "selected_ll_sample",
            None
        )

        st.session_state.pop(
            "selected_test_subpage",
            None
        )

        for i in range(20):

            st.session_state.pop(f"blows_{i}", None)
            st.session_state.pop(f"can_{i}", None)
            st.session_state.pop(f"can_weight_{i}", None)
            st.session_state.pop(f"wet_{i}", None)
            st.session_state.pop(f"dry_{i}", None)

        st.session_state.pop("active_ll_submission", None)

        st.rerun()

    st.title(
        f"Liquid Limit - {sample['sample_id']}"
    )

    st.write(
        f"Depth : {sample['depth']} m"
    )

    st.write(
        f"Sample Type : {sample['sample_type']}"
    )

    st.divider()
    
    submission = (
        supabase
        .table("ll_submissions")
        .select("*")
        .eq(
        "id",
        st.session_state["selected_ll_submission"]
        )
        .single()
        .execute()
    ).data
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

    if st.session_state.get("active_ll_submission") != current_submission:

        st.session_state["active_ll_submission"] = current_submission

        for i in range(20):

            st.session_state.pop(f"blows_{i}", None)
            st.session_state.pop(f"can_{i}", None)
            st.session_state.pop(f"can_weight_{i}", None)
            st.session_state.pop(f"wet_{i}", None)
            st.session_state.pop(f"dry_{i}", None)

        st.rerun()
    if "selected_ll_submission" not in st.session_state:

        st.session_state.pop("selected_test_subpage", None)

        st.warning("Please select a sample first.")

        st.stop()
    submission = (
        supabase
        .table("ll_submissions")
        .select("*")
        .eq(
            "id",
            st.session_state["selected_ll_submission"]
        )
        .single()
        .execute()
    ).data
    # ==========================================
# LOAD SAVED TRIALS
# ==========================================

    saved_trials = (

        supabase
        .table("ll_trials")
        .select("*")
        .eq(
            "submission_id",
            submission["id"]
        )
        .order(
            "trial_no"
        )
        .execute()

    ).data
    # st.write("Submission ID:", submission["id"])
    # st.write("Submission Status:", submission["status"])
    # st.write("Saved Trials Count:", len(saved_trials))
    # st.write(saved_trials)
    # st.stop() 
    existing_map = {

        row["trial_no"]: row

        for row in saved_trials

        }

    read_only = (

        submission["status"] == "Submitted"

        and

        submission["review_status"] != "Returned"

    )
    if saved_trials:

        st.session_state.ll_trial_count = max(
            DEFAULT_TRIALS,
            len(saved_trials)
        )

    # ------------------------
    # Dynamic Trial Count
    # ------------------------

    if "ll_trial_count" not in st.session_state:

        st.session_state.ll_trial_count = DEFAULT_TRIALS

    trial_count = st.session_state.ll_trial_count

    results = []

    # ------------------------
    # Trial Cards
    # ------------------------

    for i in range(trial_count):

        with st.container(border=True):

            c1, c2 = st.columns([5,1])

            with c1:

                st.markdown(
                    f"### Trial {i+1}"
                )

            with c2:

                if i >= DEFAULT_TRIALS:

                    if st.button(
                        "🗑",
                       key=f"delete_{i}",
                        disabled=read_only
                    ):

                        st.session_state.ll_trial_count -= 1
                        st.rerun()

        left, right = st.columns(2)
        saved = existing_map.get(
            i + 1,
            {}
        )
        trial_locked = saved.get("locked", False)

        # New submission (trial not yet saved)
        if not saved:
            trial_locked = False

        read_only = trial_locked
        with left:

            blows = st.number_input(
                "Number of Blows",
                min_value=0,
                value=int(saved.get("blows", 0)),
                step=1,
                key=f"blows_{i}",
                disabled=read_only
            )

            can_no = st.text_input(
                "Container Number",
                value=saved.get(
                    "can_no",
                    ""
                ),
                key=f"can_{i}",
                disabled=read_only
            )       

            can_weight = st.number_input(
                "Container Weight (g)",
                min_value=0.0,
                step=0.01,
                format="%.2f",
                key=f"can_weight_{i}",
                disabled=read_only,
                value=saved.get(
                    "can_weight",
                    0.0
                )
            )

        with right:

            wet = st.number_input(

                "Wet Soil + Container (g)",

                min_value=0.0,

                value=float(
                    saved.get(
                        "wet_soil_can",
                        0
                    )
                ),

                step=0.01,

                format="%.2f",

                key=f"wet_{i}",
                disabled=read_only

            )

            dry = st.number_input(
                "Dry Soil + Container (g)",
                min_value=0.0,
                value=float(
                    saved.get(
                        "dry_soil_can",
                        0
                    )
                ),  
                step=0.01,
                format="%.2f",
                key=f"dry_{i}", 
                disabled=read_only
            )

            wc = calculate_water_content(

                can_weight,

                wet,

                dry

            )

            st.markdown("---")

            if wc is None:

                st.info(
                    "Water Content : --"
                )

            else:

                st.success(

                    f"Water Content : {wc['water_content']:.2f} %"

                )

                c1, c2 = st.columns(2)
                

                with c1:

                    st.caption(

                        f"Water Weight : {wc['water_weight']:.2f} g"

                    )

                with c2:

                    st.caption(

                        f"Dry Soil : {wc['dry_soil_weight']:.2f} g"

                    )
            results.append({

                "trial_no": i+1,

                "blows": blows,

                "can_no": can_no,

                "can_weight": can_weight,

                "wet_soil_can": wet,

                "dry_soil_can": dry,

                "water_content":

        None if wc is None else wc["water_content"]

            })
            st.write("")

    # ------------------------
    # Add Trial
    # ------------------------

    if st.button(

        "➕ Add Another Trial",

        use_container_width=True,
        disabled= read_only

    ):

        st.session_state.ll_trial_count += 1

        st.rerun()

    st.divider()
    #  Calculate LL

    ll = calculate_liquid_limit(
            results
        )

    c1, c2 = st.columns(2)

    with c1:

        st.metric(

            "Liquid Limit",

            "--" if ll["liquid_limit"] is None else f"{ll['liquid_limit']:.2f} %"

        )

    with c2:

        st.metric(

            "Flow Index",

            "--" if ll["flow_index"] is None else f"{ll['flow_index']:.2f}"

        )
        # st.error("REACHED GRAPH SECTION")

    # =========================================
    # FLOW CURVE
    # =========================================

    # st.divider()
    show_spline = st.toggle(
            "Show Smoothed Flow Curve",
            value=True
        )
    from tests.liquid_limit.report import render_report

    render_report(results, show_spline=show_spline)
    

    st.divider()

    c1, c2 = st.columns(2)

# ======================================================
# SAVE DRAFT
# ======================================================

    with c1:

        if st.button(
            "💾 Save Draft",
            use_container_width=True
        ):

            valid_trials = [
                row
                for row in results
                if row["blows"] > 0 and row["water_content"] is not None
            ]

            for row in valid_trials:

                saved = existing_map.get(row["trial_no"])

                if saved:

                    (
                        supabase
                        .table("ll_trials")
                        .update({
                            "blows": row["blows"],
                            "can_no": row["can_no"],
                            "can_weight": row["can_weight"],
                            "wet_soil_can": row["wet_soil_can"],
                            "dry_soil_can": row["dry_soil_can"],
                            "water_content": row["water_content"],
                        })
                        .eq("id", saved["id"])
                        .execute()
                    )

                else:

                    (
                        supabase
                        .table("ll_trials")
                        .insert({
                            "submission_id": submission["id"],
                            "trial_no": row["trial_no"],
                            "blows": row["blows"],
                            "can_no": row["can_no"],
                            "can_weight": row["can_weight"],
                            "wet_soil_can": row["wet_soil_can"],
                            "dry_soil_can": row["dry_soil_can"],
                            "water_content": row["water_content"],
                            "approval_status": "Draft",
                            "reviewer_comments": "",
                            "locked": False
                        })
                        .execute()
                    )

            (
                supabase
                .table("ll_submissions")
                .update({
                    "status": "Draft",
                    "review_status": "Draft",
                    "liquid_limit": ll["liquid_limit"],
                    "flow_index": ll["flow_index"]
                })
                .eq("id", submission["id"])
                .execute()
            )
            for i in range(20):

                st.session_state.pop(f"blows_{i}", None)
                st.session_state.pop(f"can_{i}", None)
                st.session_state.pop(f"can_weight_{i}", None)
                st.session_state.pop(f"wet_{i}", None)
                st.session_state.pop(f"dry_{i}", None)
            st.success("Draft Saved")


    # ======================================================
    # FINAL SUBMIT
    # ======================================================

    with c2:

        if st.button(
            "✅ Final Submit",
            use_container_width=True
        ):

            valid_trials = [
                row
                for row in results
                if row["blows"] > 0 and row["water_content"] is not None
            ]

            for row in valid_trials:

                saved = existing_map.get(row["trial_no"])

                if saved:

                    update_data = {
                        "blows": row["blows"],
                        "can_no": row["can_no"],
                        "can_weight": row["can_weight"],
                        "wet_soil_can": row["wet_soil_can"],
                        "dry_soil_can": row["dry_soil_can"],
                        "water_content": row["water_content"],
                    }

                    if saved.get("approval_status") == "Returned":
                        update_data["approval_status"] = "Pending"
                        update_data["reviewer_comments"] = ""
                        update_data["locked"] = True

                    (
                        supabase
                        .table("ll_trials")
                        .update(update_data)
                        .eq("id", saved["id"])
                        .execute()
                    )

                else:

                    (
                        supabase
                        .table("ll_trials")
                        .insert({
                            "submission_id": submission["id"],
                            "trial_no": row["trial_no"],
                            "blows": row["blows"],
                            "can_no": row["can_no"],
                            "can_weight": row["can_weight"],
                            "wet_soil_can": row["wet_soil_can"],
                            "dry_soil_can": row["dry_soil_can"],
                            "water_content": row["water_content"],
                            "approval_status": "Pending",
                            "reviewer_comments": "",
                            "locked": True
                        })
                        .execute()
                    )

            (
                supabase
                .table("ll_submissions")
                .update({
                    "status": "Submitted",
                    "review_status": "Pending",
                    "liquid_limit": ll["liquid_limit"],
                    "flow_index": ll["flow_index"]
                })
                .eq("id", submission["id"])
                .execute()
            )

            existing_review = (
                supabase
                .table("reviews")
                .select("*")
                .eq("project_id", st.session_state["selected_project"])
                .eq("borehole_id", sample["borehole_id"])
                .eq("test_name", "Liquid Limit")
                .execute()
            ).data

            if not existing_review:

                (
                    supabase
                    .table("reviews")
                    .insert({
                        "project_id": st.session_state["selected_project"],
                        "borehole_id": sample["borehole_id"],
                        "test_name": "Liquid Limit",
                        "status": "Pending"
                    })
                    .execute()
                )

            st.success("Submitted for Review")
            for i in range(20):

                st.session_state.pop(f"blows_{i}", None)
                st.session_state.pop(f"can_{i}", None)
                st.session_state.pop(f"can_weight_{i}", None)
                st.session_state.pop(f"wet_{i}", None)
                st.session_state.pop(f"dry_{i}", None)

            st.session_state.pop("active_ll_submission", None)
            st.rerun()