import streamlit as st
import pandas as pd
from tests.ucs.calculations import (
    calculate_ld_ratio,
    calculate_area,
    calculate_volume,
    calculate_bulk_density,
    calculate_ucs
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

    st.title("Unconfined Compressive Strength")
    # st.success("THIS IS UCS ENTRY")

        # st.write(f"Project ID : {project_id}")
        # st.write(f"Borehole ID : {borehole_id}")

    st.divider()

    # ---------------------------------
    # Find / Create Submission
    # ---------------------------------

    result = (
        supabase
        .table("ucs_submissions")
        .select("*")
        .eq("project_id", project_id)
        .eq("borehole_id", borehole_id)
        .limit(1)
        .execute()
    ).data

    if result:

        submission = result[0]

    else:

        submission = (
            supabase
            .table("ucs_submissions")
            .insert({
                "project_id": project_id,
                "borehole_id": borehole_id,
                "status": "Draft",
                "review_status": "Draft"
            })
            .execute()
        ).data[0]

    st.session_state["selected_ucs_submission"] = submission["id"]
    current_submission = submission["id"]
    saved_rows = (
        supabase
        .table("ucs_specimens")
        .select("*")
        .eq("submission_id", submission["id"])
        .order("specimen_no")
        .execute()
    ).data
    # st.write(saved_rows)
    read_only = (
        submission["review_status"] == "Pending"
        or submission["review_status"] == "Approved"
    )

    # ---------------------------------
    # Initialize DataFrame
    # ---------------------------------

    if (
        "ucs_df" not in st.session_state
        or st.session_state.get("ucs_submission_loaded") != current_submission
    ):
        if saved_rows:
  
            # if True:
                    st.session_state.ucs_df = pd.DataFrame([
                  {
            
                    "Select": False,

                    "From": row["from_depth"],
                    "To": row["to_depth"],

                    "Rock Number": row["rock_number"],

                    "Diameter": row["diameter"],
                    "Length": row["length"],

                    "L/D Ratio": row["ld_ratio"],
                    "Area": row["area"],
                    "Volume": row["volume"],

                    "Weight": row["weight"],

                    "Bulk Density": row["bulk_density"],

                    "Failure Load": row["failure_load"],

                    "UCS": row["ucs"],

                    "Remarks": row["remarks"]

                }
                for row in saved_rows
            ])

        else:

            st.session_state.ucs_df = pd.DataFrame([
                {
                                       "Select": False,

                    "From": None,
                    "To": None,

                    "Rock Number": "",

                    "Diameter": None,
                    "Length": None,

                    "L/D Ratio": None,
                    "Area": None,
                    "Volume": None,

                    "Weight": None,

                    "Bulk Density": None,

                    "Failure Load": None,

                    "UCS": None,

                    "Remarks": ""
                }
            ])

    # ---------------------------------
    # Buttons
    # ---------------------------------

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

                    "Diameter": None,
                    "Length": None,

                    "L/D Ratio": None,
                    "Area": None,
                    "Volume": None,

                    "Weight": None,

                    "Bulk Density": None,

                    "Failure Load": None,

                    "UCS": None,

                    "Remarks": ""
                }

            st.session_state.ucs_df.loc[
                len(st.session_state.ucs_df)
            ] = new_row

            st.rerun()

    with c2:

        if st.button(
            "🗑 Remove Selected",
            use_container_width=True
        ):

            df = st.session_state.ucs_df

            df = df[df["Select"] == False].reset_index(drop=True)

            if df.empty:

                df = pd.DataFrame([{
                                        "Select": False,

                    "From": None,
                    "To": None,

                    "Rock Number": "",

                    "Diameter": None,
                    "Length": None,

                    "L/D Ratio": None,
                    "Area": None,
                    "Volume": None,

                    "Weight": None,

                    "Bulk Density": None,

                    "Failure Load": None,

                    "UCS": None,

                    "Remarks": ""
            
                }])

            st.session_state.ucs_df = df

            st.rerun()
        
    st.session_state.ucs_submission_loaded = current_submission
    # st.write(st.session_state.ucs_df.columns.tolist())

    # ---------------------------------
    # Editable Table
    # ---------------------------------

    edited_df = st.data_editor(
    st.session_state.ucs_df,
    use_container_width=True,
    disabled=read_only,
    hide_index=True,
    key="ucs_editor",
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

        "Diameter": st.column_config.NumberColumn(
            "Diameter (cm)",
            format="%.2f"
        ),

        "Length": st.column_config.NumberColumn(
            "Length (cm)",
            format="%.2f"
        ),

        "L/D Ratio": st.column_config.NumberColumn(
            "L/D Ratio",
            format="%.2f",
            disabled=True
        ),

        "Area": st.column_config.NumberColumn(
            "Area (cm²)",
            format="%.2f",
            disabled=True
        ),

        "Volume": st.column_config.NumberColumn(
            "Volume (cm³)",
            format="%.2f",
            disabled=True
        ),

        "Weight": st.column_config.NumberColumn(
            "Weight (g)",
            format="%.2f"
        ),

        "Bulk Density": st.column_config.NumberColumn(
            "Bulk Density (g/cc)",
            format="%.3f",
            disabled=True
        ),

        "Failure Load": st.column_config.NumberColumn(
            "Failure Load (kN)",
            format="%.2f"
        ),

        "UCS": st.column_config.NumberColumn(
            "UCS (MPa)",
            format="%.2f",
            disabled=True
        ),

        "Remarks": st.column_config.TextColumn(
            "Remarks"
        )
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

                ld_ratio = calculate_ld_ratio(
                    row["Length"],
                    row["Diameter"]
                )

                area = calculate_area(
                    row["Diameter"]
                )

                volume = calculate_volume(
                    area,
                    row["Length"]
                )

                bulk_density = calculate_bulk_density(
                    row["Weight"],
                    volume
                )

                ucs = calculate_ucs(
                    row["Failure Load"],
                    area
                )

                df.at[index, "L/D Ratio"] = ld_ratio
                df.at[index, "Area"] = area
                df.at[index, "Volume"] = volume
                df.at[index, "Bulk Density"] = bulk_density
                df.at[index, "UCS"] = ucs

            st.session_state.ucs_df = df

            # -----------------------------
            # Delete old rows
            # -----------------------------

            (
                supabase
                .table("ucs_specimens")
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
                    .table("ucs_specimens")
                    .insert({

                        "submission_id": submission["id"],

                        "specimen_no": specimen_no,

                        "from_depth": row["From"],
                        "to_depth": row["To"],

                        "rock_number": row["Rock Number"],

                        "diameter": row["Diameter"],
                        "length": row["Length"],

                        "ld_ratio": row["L/D Ratio"],
                        "area": row["Area"],
                        "volume": row["Volume"],

                        "weight": row["Weight"],
                        "bulk_density": row["Bulk Density"],

                        "failure_load": row["Failure Load"],

                        "ucs": row["UCS"],

                        "remarks": row["Remarks"],

                        "approval_status": "Draft",

                        "locked": False

                    })
                    .execute()
                )

            (
                supabase
                .table("ucs_submissions")
                .update({
                    "status": "Draft",
                    "review_status": "Draft"
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

                ld_ratio = calculate_ld_ratio(
                    row["Length"],
                    row["Diameter"]
                )

                area = calculate_area(
                    row["Diameter"]
                )

                volume = calculate_volume(
                    area,
                    row["Length"]
                )

                bulk_density = calculate_bulk_density(
                    row["Weight"],
                    volume
                )

                ucs = calculate_ucs(
                    row["Failure Load"],
                    area
                )

                df.at[index, "L/D Ratio"] = ld_ratio
                df.at[index, "Area"] = area
                df.at[index, "Volume"] = volume
                df.at[index, "Bulk Density"] = bulk_density
                df.at[index, "UCS"] = ucs

            st.session_state.ucs_df = df
            (
                supabase
                .table("ucs_specimens")
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
                    .table("ucs_specimens")
                    .insert({

                        "submission_id": submission["id"],

                        "specimen_no": specimen_no,

                        "from_depth": row["From"],
                        "to_depth": row["To"],

                        "rock_number": row["Rock Number"],

                        "diameter": row["Diameter"],
                        "length": row["Length"],

                        "ld_ratio": row["L/D Ratio"],
                        "area": row["Area"],
                        "volume": row["Volume"],

                        "weight": row["Weight"],
                        "bulk_density": row["Bulk Density"],

                        "failure_load": row["Failure Load"],

                        "ucs": row["UCS"],

                        "remarks": row["Remarks"],

                        "approval_status": "Draft",

                        "locked": False

                    })
                    .execute()
                    
                )
                # st.write("Insert Result:", row["Rock Number"])
            (
                supabase
                .table("ucs_submissions")
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
                .eq("test_name", "Unconfined Compressive Test")
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

                        "test_name": "Unconfined Compressive Test",

                        "status": "Pending"

                    })
                    .execute()
                )
                st.success("UCS submitted successfully.")
                st.rerun()