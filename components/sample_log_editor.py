import streamlit as st
import pandas as pd

from utils.sample_log import (


    save_sample_log,

    delete_sample_log,

    generate_sample_log

)

from utils.database import get_supabase

supabase = get_supabase()
def render(
    borehole,
    samples
):

    

    st.subheader(
        "Sample Log"
    )

    if not samples:

        st.info(
            "No Samples Found"
        )

        return

    df = pd.DataFrame(
        samples
    )

    # if "remarks" not in df.columns:

    #     df["remarks"] = ""

    for col in [

        "remarks",

        "spt_n_value",

        "bulk_density",

        "dry_unit_weight",

        "insitu_water_content"

    ]:

        if col not in df.columns:

            df[col] = None

    df = df[
        [
            "sample_id",
            
            "depth",

            "sample_type",

            "spt_n_value",

            "bulk_density",

            "dry_unit_weight",

            "insitu_water_content",

            "remarks"

        ]
    ]

    edited = st.data_editor(

    df,

    column_config={
        "sample_id":

            st.column_config.TextColumn(
                "Sample ID",
                disabled=True
            ),
        "depth": st.column_config.NumberColumn(

            "Depth (m)",

            step=0.1

        ),

        "sample_type":

        st.column_config.SelectboxColumn(

            "Sample Type",

            options=[

                "SPT",

                "UDS",

                "DS",

                "Manual Sample",

                "CORE",

                "Water Sample",

                "Rock Sample",

                "Other"

            ]

        ),

        "spt_n_value":

        st.column_config.NumberColumn(
            "SPT-N"
        ),

        "bulk_density":

        st.column_config.NumberColumn(
            "Bulk Density"
        ),

        "dry_unit_weight":

        st.column_config.NumberColumn(
            "Dry Unit Weight"
        ),

        "insitu_water_content":

        st.column_config.NumberColumn(
            "Water Content (%)"
        ),

        "remarks":

        st.column_config.TextColumn(
            "Remarks"
        )

    },

    num_rows="dynamic",

    use_container_width=True

)

    c1, c2 = st.columns(2)

    with c1:

        if st.button(
            "Save Sample Log",
            key=f"save_log_{borehole['id']}"
        ):

            if edited.empty:

                st.error(
                    "Sample Log Empty"
                )

                st.stop()

            edited = edited.sort_values(
                "depth"
            )

            if edited[
                "depth"
            ].duplicated().any():

                st.error(
                    "Duplicate Depths Found"
                )

                st.stop()

            save_sample_log(

                borehole["id"],

                edited.to_dict(
                    "records"
                )

            )

            st.success(
                "Sample Log Saved"
            )

            st.cache_data.clear()
            st.rerun()

    with c2:
        if st.button(
        "Regenerate",
        key=f"regen_{borehole['id']}"
    ):
            st.session_state[
                f"confirm_regen_{borehole['id']}"
            ] = True
        if st.session_state.get(
            f"confirm_regen_{borehole['id']}",
            False
        ):

                st.warning(
                    "⚠️ Regenerating the sample log will delete the existing sample log and create a new one."
                )

                c1, c2 = st.columns(2)

                with c1:

                    if st.button(
                        "✅ Regenerate",
                        key=f"confirm_regen_btn_{borehole['id']}"
                    ):
                            # =====================================
                            # CHECK FOR EXISTING TEST DATA
                            # =====================================

                            tables = [
                                "ll_submissions",
                                "pl_submissions",
                                "specific_gravity_submissions",
                                "ds_submissions",
                                "gsa_submissions"
                            ]

                            has_data = False

                            for table in tables:

                                result = (
                                    supabase
                                    .table(table)
                                    .select("id")
                                    .eq(
                                        "borehole_id",
                                        borehole["id"]
                                    )
                                    .limit(1)
                                    .execute()
                                )

                                if result.data:

                                    has_data = True
                                    break


                            if has_data:

                                st.error(
                                    "Cannot regenerate sample log because laboratory test data already exists for this borehole."
                                )

                                st.session_state.pop(
                                    f"confirm_regen_{borehole['id']}",
                                    None
                                )

                                st.stop()


                            delete_sample_log(
                                borehole["id"]
                            )

                        

                            generate_sample_log(

                            borehole["id"],

                            borehole["depth"],

                            borehole[
                                "first_sample_depth"
                            ],

                            borehole[
                                "first_sample_type"
                            ]

                        )

                            st.session_state.pop(
                                f"confirm_regen_{borehole['id']}",
                                None
                            )

                            st.success(
                                "Sample log regenerated."
                            )

                            st.cache_data.clear()
                            st.rerun()

                    with c2:

                        if st.button(
                            "❌ Cancel",
                            key=f"cancel_regen_{borehole['id']}"
                        ):

                            st.session_state.pop(
                                f"confirm_regen_{borehole['id']}",
                                None
                            )

                            st.rerun()          
