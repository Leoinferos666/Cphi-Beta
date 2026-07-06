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

                "Core",

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

            st.success(
                "Log Regenerated"
            )

            st.cache_data.clear()
            st.rerun()

