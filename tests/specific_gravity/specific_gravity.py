import streamlit as st
from utils.database import supabase

def render():
                # st.set_page_config(
                #     page_title="Specific Gravity Test",
                #     layout="wide"
                # )

                # =====================================
                # VALIDATION
                # =====================================

                if "selected_project" not in st.session_state:
                    st.error("No Project Selected")
                    st.stop()

                if "selected_borehole" not in st.session_state:
                    st.error("No Borehole Selected")
                    st.stop()

                project_id = st.session_state["selected_project"]
                borehole_id = st.session_state["selected_borehole"]

                # =====================================
                # LOAD PROJECT
                # =====================================

                project = (
                    supabase
                    .table("projects")
                    .select("*")
                    .eq("id", project_id)
                    .single()
                    .execute()
                ).data

                # =====================================
                # LOAD BOREHOLE
                # =====================================

                borehole = (
                    supabase
                    .table("boreholes")
                    .select("*")
                    .eq("id", borehole_id)
                    .single()
                    .execute()
                ).data

                # =====================================
                # FIND OR CREATE SUBMISSION
                # =====================================

                submission = (
                    supabase
                    .table("specific_gravity_submissions")
                    .select("*")
                    .eq("project_id", project_id)
                    .eq("borehole_id", borehole_id)
                    .execute()
                )

                if submission.data:

                    submission_id = submission.data[0]["id"]

                else:

                    response = (
                        supabase
                        .table("specific_gravity_submissions")
                        .insert({
                            "project_id": project_id,
                            "borehole_id": borehole_id,
                            "status": "Draft",
                            "is_locked": False
                        })
                        .execute()
                    )

                    submission_id = response.data[0]["id"]

                # =====================================
                # LOAD SUBMISSION
                # =====================================

                submission_record = (
                    supabase
                    .table("specific_gravity_submissions")
                    .select("*")
                    .eq("id", submission_id)
                    .single()
                    .execute()
                ).data

                # =====================================
                # HEADER
                # =====================================

                col1, col2 = st.columns([1, 5])

                with col1:

                    if st.button("⬅ Back"):

                        st.switch_page(
                            "pages/02_Project.py"
                        )

                with col2:

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
                # ADD DEPTH
                # =====================================

                if submission_record["status"] == "Draft":

                    st.subheader(
                        "Add Depth Sample"
                    )

                    with st.form("depth_form"):

                        depth = st.number_input(
                            "Depth (m)",
                            min_value=0.0,
                            step=0.1,
                            format="%.2f"
                        )

                        add_depth = st.form_submit_button(
                            "Add Depth"
                        )

                        if add_depth:

                            existing = (
                                supabase
                                .table("specific_gravity_depths")
                                .select("*")
                                .eq(
                                    "submission_id",
                                    submission_id
                                )
                                .eq(
                                    "depth",
                                    depth
                                )
                                .execute()
                            )

                            if existing.data:

                                st.warning(
                                    "Depth already exists"
                                )

                            else:

                                (
                                    supabase
                                    .table("specific_gravity_depths")
                                    .insert({

                                        "submission_id":
                                        submission_id,

                                        "depth":
                                        depth

                                    })
                                    .execute()
                                )

                                st.success(
                                    "Depth Added"
                                )

                                st.rerun()

                # =====================================
                # LOAD DEPTHS
                # =====================================

                depths = (
                    supabase
                    .table("specific_gravity_depths")
                    .select("*")
                    .eq(
                        "submission_id",
                        submission_id
                    )
                    .order("depth")
                    .execute()
                )

                # =====================================
                # DEPTH LIST
                # =====================================

                st.subheader(
                    "Depth Samples"
                )

                if not depths.data:

                    st.info(
                        "No Depth Samples Added Yet"
                    )

                else:

                    for depth_row in depths.data:

                        trial_count = (
                            supabase
                            .table("specific_gravity_tests")
                            .select("*", count="exact")
                            .eq(
                                "depth_id",
                                depth_row["id"]
                            )
                            .execute()
                        )

                        with st.container(border=True):

                            c1, c2, c3 = st.columns([4,1,1])

                            with c1:

                                st.write(
                                    f"### Depth {depth_row['depth']} m"
                                )

                                if trial_count.count == 3:

                                    st.success(
                                        "Observations Saved"
                                    )

                                else:

                                    st.warning(
                                        "Pending Observations"
                                    )

                            with c2:

                                if (
                                    submission_record["status"]
                                    == "Draft"
                                ):

                                    if st.button(
                                        "Open",
                                        key=f"open_{depth_row['id']}"
                                    ):

                                        st.session_state[
                                            "selected_sg_depth"
                                        ] = depth_row["id"]

                                        st.switch_page(
                                            "pages/04_SG_Depth.py"
                                        )

                            with c3:

                                if (
                                    submission_record["status"]
                                    == "Draft"
                                ):

                                    if st.button(
                                        "Delete",
                                        key=f"delete_{depth_row['id']}"
                                    ):

                                        (
                                            supabase
                                            .table(
                                                "specific_gravity_depths"
                                            )
                                            .delete()
                                            .eq(
                                                "id",
                                                depth_row["id"]
                                            )
                                            .execute()
                                        )

                                        st.rerun()

                # =====================================
                # FINAL SUBMIT
                # =====================================

                all_complete = True

                for depth_row in depths.data:

                    trials = (
                        supabase
                        .table("specific_gravity_tests")
                        .select("*", count="exact")
                        .eq(
                            "depth_id",
                            depth_row["id"]
                        )
                        .execute()
                    )

                    if trials.count != 3:

                        all_complete = False

                if (
                    submission_record["status"] == "Draft"
                    and len(depths.data) > 0
                ):

                    st.divider()

                    if not all_complete:

                        st.warning(
                            "Complete all depth samples before final submission."
                        )

                    else:

                        if st.button(
                            "Final Submit Test",
                            type="primary",
                            use_container_width=True
                        ):

                            for depth_row in depths.data:

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
                                    .execute()
                                )

                                for row in trials.data:

                                    denominator = (
                                        (row["m4"] - row["m1"])
                                        -
                                        (row["m3"] - row["m2"])
                                    )

                                    if denominator > 0:

                                        sg = (
                                            (row["m2"] - row["m1"])
                                            /
                                            denominator
                                        )

                                        (
                                            supabase
                                            .table(
                                                "specific_gravity_tests"
                                            )
                                            .update({

                                                "specific_gravity":
                                                round(
                                                    sg,
                                                    3
                                                ),

                                                "status":
                                                "Submitted",

                                                "locked":
                                                True

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
                                    True

                                })
                                .eq(
                                    "id",
                                    submission_id
                                )
                                .execute()
                            )

                            st.success(
                                "Specific Gravity Test Submitted"
                            )

                            st.rerun()

                # =====================================
                # RESULTS
                # =====================================

                if submission_record["status"] == "Submitted":

                    st.divider()

                    st.subheader(
                        "Results"
                    )

                    for depth_row in depths.data:

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

                            st.write(
                                f"### Depth {depth_row['depth']} m"
                            )

                            values = []

                            for trial in trials.data:

                                values.append(
                                    trial["specific_gravity"]
                                )

                                st.write(
                                    f"Trial {trial['trial_no']} : {trial['specific_gravity']}"
                                )

                            avg = (
                                sum(values)
                                /
                                len(values)
                            )

                            st.success(
                                f"Average Specific Gravity : {avg:.2f}"
                            )