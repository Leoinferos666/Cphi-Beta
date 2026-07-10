import streamlit as st
import pandas as pd
from tests.point_load.calculations import (
    STANDARD_CORE_DIAMETER,
    calculate_load_kn,
    calculate_failure_load,
    calculate_d_factor,
    calculate_is50,
    calculate_qc
)
from utils.database import get_supabase

supabase = get_supabase()


def render():

    # ---------------------------------
    # Check selected borehole
    # ---------------------------------

    if "selected_borehole" not in st.session_state:
        st.error("No Borehole Selected")
        st.stop()

    project_id = st.session_state["selected_project"]
    borehole_id = st.session_state["selected_borehole"]

    # ---------------------------------
    # Header
    # ---------------------------------

    st.title("Point Load Strength Index Test")

    # st.write(f"Project ID : {project_id}")
    # st.write(f"Borehole ID : {borehole_id}")

    st.divider()
    # ---------------------------------
    # Dial Gauge Constant
    # ---------------------------------
    if "point_load_dial_constant" not in st.session_state:
        st.session_state.point_load_dial_constant = 1.0
    st.session_state.point_load_dial_constant = st.number_input(
        "Dial Gauge Constant (kN/div)",
        min_value=0.0,
        value=float(st.session_state.point_load_dial_constant),
        step=0.01,
    )


    # ---------------------------------
    # Find / Create Submission
    # ---------------------------------

    result = (
        supabase
        .table("point_load_submissions")
        .select("*")
        .eq("project_id", project_id)
        .eq("borehole_id", borehole_id)
        .limit(1)
        .execute()
    ).data

    if result:

        submission = result[0]
        st.session_state.point_load_dial_constant = (
            submission.get("dial_gauge_constant")
            or 1.0
        )

    else:

        submission = (
            supabase
            .table("point_load_submissions")
            .insert({
                "project_id": project_id,
                "borehole_id": borehole_id,
                "status": "Draft",
                "review_status": "Draft",
                "dial_gauge_constant": 1.0
            })
            .execute()
        ).data[0]

    st.session_state["selected_point_load_submission"] = submission["id"]
    current_submission = submission["id"]
    saved_rows = (
        supabase
        .table("point_load_specimens")
        .select("*")
        .eq("submission_id", submission["id"])
        .order("specimen_no")
        .execute()
    ).data
    read_only = (
        submission["review_status"] == "Pending"
        or submission["review_status"] == "Approved"
    )

    # ---------------------------------
    # Initialize DataFrame
    # ---------------------------------

    if (
    "point_load_df" not in st.session_state
    or
    st.session_state.get("point_load_submission_loaded")
    != current_submission
):

        if saved_rows:

            st.session_state.point_load_df = pd.DataFrame([
                {
                    "Select": False,
                    "From": row["depth_from"],
                    "To": row["depth_to"],
                    "Rock Number": row["rock_number"],
                    "Std. Core Diameter": row["standard_core_diameter"],
                    "Diameter": row["diameter"],
                    "D¹·⁵ × D*⁰·⁵": row.get("d_factor"),
                    "Length": row["length"],
                    "Width": row["width"],
                    "Test Type": row["test_type"],
                    "Dial Gauge": row["dial_gauge"],
                    "Load (kN)": row.get("load_kn"),
                    "Failure Load": row["failure_load"],
                    "Is50": row["is50"],
                    "qc": row["qc"],
                }
                for row in saved_rows
            ])

        else:

            st.session_state.point_load_df = pd.DataFrame([
                {
                    "Select": False,
                    "From": None,
                    "To": None,
                    "Rock Number": "",
                    "Std. Core Diameter": 50.0,
                    "Diameter": None,
                    "D¹·⁵ × D*⁰·⁵": None,
                    "Length": None,
                    "Width": None,
                    "Test Type": "Diametral",
                    "Dial Gauge": None,
                    "Load (kN)": None,
                    "Failure Load": None,
                    "Is50": None,
                    "qc": None,
                }
            ])

    # ---------------------------------
    # Buttons
    # ---------------------------------

   

    # with c2:

    #     if st.button(
    #         "🗑 Remove Selected",
    #         use_container_width=True
    #     ):

    #         df = st.session_state.point_load_df

    #         df = df[df["Select"] == False].reset_index(drop=True)

    #         if df.empty:

    #             df = pd.DataFrame([{
    #                 "Select": False,
    #                 "From": None,
    #                 "To": None,
    #                 "Rock Number": "",
    #                 "Diameter": None,
    #                 "Std. Core Diameter": 50.0,
    #                 "D¹·⁵ × D*⁰·⁵": None,
    #                 "Length": None,
    #                 "Width": None,
    #                 "Test Type": "Diametral",
    #                 "Dial Gauge": None,
    #                 "Load (kN)": None,
    #                 "Failure Load": None,
    #                 "Is50": None,
    #                 "qc": None,
    #             }])

    #         st.session_state.point_load_df = df

    #         st.rerun()
        
    st.session_state.point_load_submission_loaded = current_submission
    c1, c2 = st.columns(2)

    with c1:

        if st.button(
            "➕ Add Row",
            use_container_width=True
        ):

            new_row = {
                "Select": False,
                "From": None,
                "To": None,
                "Rock Number": "",
                "Std. Core Diameter": 50.0,
                "Diameter": None,
                "D¹·⁵ × D*⁰·⁵": None,
                "Length": None,
                "Width": None,
                "Test Type": "Diametral",
                "Dial Gauge": None,
                "Load (kN)": None,
                "Failure Load": None,
                "Is50": None,
                "qc": None,
            }

            st.session_state.point_load_df.loc[
                len(st.session_state.point_load_df)
            ] = new_row

            st.rerun()

    with c2:

        if st.button(
            "🗑 Remove Selected",
            use_container_width=True
        ):

            edited_rows = st.session_state.get(
                "point_load_editor",
                {}
            ).get(
                "edited_rows",
                {}
            )

            df = st.session_state.point_load_df.copy()

            for row_index, changes in edited_rows.items():

                for column, value in changes.items():

                    df.at[row_index, column] = value

            df = df[df["Select"] == False].reset_index(drop=True)

            if df.empty:

                df = pd.DataFrame([{
                    "Select": False,
                    "From": None,
                    "To": None,
                    "Rock Number": "",
                    "Std. Core Diameter": 50.0,
                    "Diameter": None,
                    "D¹·⁵ × D*⁰·⁵": None,
                    "Length": None,
                    "Width": None,
                    "Test Type": "Diametral",
                    "Dial Gauge": None,
                    "Load (kN)": None,
                    "Failure Load": None,
                    "Is50": None,
                    "qc": None,
                }])

            st.session_state.point_load_df = df

            st.rerun()
    # ---------------------------------
    # Editable Table
    # ---------------------------------
    # st.write(st.session_state.point_load_df.columns.tolist())
    edited_df = st.data_editor(
    
        
    st.session_state.point_load_df,
    use_container_width=True,
    disabled=read_only,
    hide_index=True,
    key="point_load_editor",
    column_config={

        "Select": st.column_config.CheckboxColumn(
            "✓"
        ),

        "From": st.column_config.NumberColumn(
            "From (m)",
            format="%.2f"
        ),

        "To": st.column_config.NumberColumn(
            "To (m)",
            format="%.2f"
        ),

        "Rock Number": st.column_config.TextColumn(
            "Rock No"
        ),
        "Std. Core Diameter": st.column_config.NumberColumn(
                    "D* (mm)",
                    format="%.2f",
                    disabled=True
                ),
        "Diameter": st.column_config.NumberColumn(
            "D (mm)",
            format="%.2f"
        ),
        "D¹·⁵ × D*⁰·⁵": st.column_config.NumberColumn(
            "D¹·⁵ × D*⁰·⁵",
            format="%.2f",
            disabled=True
        ),

        "Length": st.column_config.NumberColumn(
            "L (mm)",
            format="%.2f"
        ),

        "Width": st.column_config.NumberColumn(
            "W (mm)",
            format="%.2f"
        ),

        "Test Type": st.column_config.SelectboxColumn(
            "Test Type",
            options=[
                "Diametral",
                "Axial",
                "Block"
            ]
        ),

        "Dial Gauge": st.column_config.NumberColumn(
            "Dial",
            format="%.2f"
        ),
        "Load (kN)": st.column_config.NumberColumn(
            "Load (kN)",
            format="%.2f"
        ),
        "Failure Load": st.column_config.NumberColumn(
            "P (N)",
            format="%.2f"
        ),

        "Is50": st.column_config.NumberColumn(
            "Is(50)",
            format="%.3f",
            disabled=True
        ),

        "qc": st.column_config.NumberColumn(
            "qc",
            format="%.3f",
            disabled=True
        ),
    }
)
   
    
    if not read_only:
        
        st.divider()

        c1, c2 = st.columns(2)

        with c1:

            save_draft = st.button(
                "💾 Save Draft",
                use_container_width=True
            )

        with c2:

            final_submit = st.button(
                "✅ Final Submit",
                use_container_width=True
            )
        if save_draft:

            df = edited_df.copy()

            # -----------------------------
            # Calculate Results
            # -----------------------------

            for index, row in df.iterrows():

                df.at[index, "Std. Core Diameter"] = STANDARD_CORE_DIAMETER

                load_kn = calculate_load_kn(
                        row["Dial Gauge"],
                        st.session_state.point_load_dial_constant,
                        row["Load (kN)"]
                    )

                failure_load = calculate_failure_load(load_kn)

                d_factor = calculate_d_factor(
                        row["Diameter"],
                        row["Std. Core Diameter"]
                    )

                is50 = calculate_is50(
                        failure_load,
                        row["Diameter"]
                    )

                qc = calculate_qc(is50)

                df.at[index, "Load (kN)"] = load_kn
                df.at[index, "Failure Load"] = failure_load
                df.at[index, "D¹·⁵ × D*⁰·⁵"] = d_factor
                df.at[index, "Is50"] = is50
                df.at[index, "qc"] = qc

                st.session_state.point_load_df = df

            # -----------------------------
            # Delete old rows
            # -----------------------------

            (
                supabase
                .table("point_load_specimens")
                .delete()
                .eq("submission_id", submission["id"])
                .execute()
            )
            
            # -----------------------------
            # Insert new rows
            # -----------------------------

            for specimen_no, row in enumerate(df.to_dict("records"), start=1):
                if not row["Rock Number"]:
                    continue

                (
                    supabase
                    .table("point_load_specimens")
                    .insert({

                        "submission_id": submission["id"],

                        "specimen_no": specimen_no,

                        "depth_from": row["From"],
                        "depth_to": row["To"],

                        "rock_number": row["Rock Number"],

                        "diameter": row["Diameter"],
                        "standard_core_diameter": row["Std. Core Diameter"],

                        "length": row["Length"],
                        "width": row["Width"],

                        "test_type": row["Test Type"],

                        "dial_gauge": row["Dial Gauge"],
                        "load_kn": row["Load (kN)"],

                        "d_factor": row["D¹·⁵ × D*⁰·⁵"],

                        "failure_load": row["Failure Load"],

                        "is50": row["Is50"],

                        "qc": row["qc"],

                        "approval_status": "Draft",

                        "locked": False

                    })
                    .execute()
                )

            (
                supabase
                .table("point_load_submissions")
                .update({
                    "status": "Draft",
                    "review_status": "Draft"
                })
                .eq("id", submission["id"])
                .execute()
            )
            (
                supabase
                .table("point_load_submissions")
                .update({
                    "dial_gauge_constant":
                    st.session_state.point_load_dial_constant
                })
                .eq("id", submission["id"])
                .execute()
            )
            st.success("Draft Saved")

            st.rerun()
        if final_submit:

            df = edited_df.copy()

            # -----------------------------
            # Calculate Results
            # -----------------------------

            for index, row in df.iterrows():

                df.at[index, "Std. Core Diameter"] = STANDARD_CORE_DIAMETER

                load_kn = calculate_load_kn(
                    row["Dial Gauge"],
                    st.session_state.point_load_dial_constant,
                    row["Load (kN)"]
                )

                failure_load = calculate_failure_load(load_kn)

                d_factor = calculate_d_factor(
                    row["Diameter"],
                    row["Std. Core Diameter"]
                )

                is50 = calculate_is50(
                    failure_load,
                    row["Diameter"]
                )

                qc = calculate_qc(is50)

                df.at[index, "Load (kN)"] = load_kn
                df.at[index, "Failure Load"] = failure_load
                df.at[index, "D¹·⁵ × D*⁰·⁵"] = d_factor
                df.at[index, "Is50"] = is50
                df.at[index, "qc"] = qc
            st.session_state.point_load_df = df
            (
                supabase
                .table("point_load_specimens")
                .delete()
                .eq(
                    "submission_id",
                    submission["id"]
                )
                .execute()
            )
            for specimen_no, row in enumerate(df.to_dict("records"), start=1):

                if not row["Rock Number"]:
                    continue

                (
                    supabase
                    .table("point_load_specimens")
                    .insert({

                        "submission_id": submission["id"],

                        "specimen_no": specimen_no,

                        "depth_from": row["From"],
                        "depth_to": row["To"],

                        "rock_number": row["Rock Number"],

                        "diameter": row["Diameter"],
                        "standard_core_diameter": row["Std. Core Diameter"],

                        "length": row["Length"],
                        "width": row["Width"],

                        "test_type": row["Test Type"],

                        "dial_gauge": row["Dial Gauge"],
                        "load_kn": row["Load (kN)"],

                        "d_factor": row["D¹·⁵ × D*⁰·⁵"],    

                        "failure_load": row["Failure Load"],

                        "is50": row["Is50"],

                        "qc": row["qc"],

                        "approval_status": "Pending",

                        "locked": False

                    })
                    .execute()
                )
                (
                    supabase
                    .table("point_load_submissions")
                    .update({
                        "dial_gauge_constant":
                        st.session_state.point_load_dial_constant
                    })
                    .eq("id", submission["id"])
                    .execute()
                )
            (
                supabase
                .table("point_load_submissions")
                .update({
                    "status": "Submitted",
                    "review_status": "Pending"
                })
                .eq(
                    "id",
                    submission["id"]
                )
                .execute()
            )
            existing_review = (
                supabase
                .table("reviews")
                .select("*")
                .eq("project_id", submission["project_id"])
                .eq("borehole_id", submission["borehole_id"])
                .eq("test_name", "Point Load Strength Index")
                .execute()
            ).data
            if existing_review:

                (
                    supabase
                    .table("reviews")
                    .update({
                        "status": "Pending"
                    })
                    .eq(
                        "id",
                        existing_review[0]["id"]
                    )
                    .execute()
                )
            else:

                (
                    supabase
                    .table("reviews")
                    .insert({

                        "project_id": submission["project_id"],

                        "borehole_id": submission["borehole_id"],

                        "test_name": "Point Load Strength Index",

                        "status": "Pending"

                    })
                    .execute()
                )
                st.success("Point Load submitted successfully.")
                st.rerun()