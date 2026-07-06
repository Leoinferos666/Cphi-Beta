import streamlit as st

from utils.database import get_supabase

supabase = get_supabase()

from utils.sample_log import (
    generate_sample_log
)


def render(
    project_id
):

    st.subheader(
        "Add Borehole"
    )

    with st.form(
        "add_borehole"
    ):

        bh_no = st.text_input(
            "BH Number"
        )

        depth = st.number_input(
            "Borehole Depth (m)",
            min_value=0.0,
            value=20.0
        )

        gwt = st.number_input(
            "Ground Water Table (m)",
            min_value=0.0,
            value=0.0
        )

        location = st.text_input(
            "Location Details"
        )

        st.divider()

        first_sample_depth = (
            st.number_input(

                "First Sample Depth (m)",

                min_value=0.0,

                value=1.5,

                step=0.5

            )
        )

        first_sample_type = (
            st.selectbox(

                "First Sample Type",

                [
                    "SPT",
                    "UDS"
                ]

            )
        )

        save = st.form_submit_button(
            "Create Borehole"
        )

        if save:

            response = (

                supabase
                .table("boreholes")
                .insert({

                    "project_id":
                    project_id,

                    "bh_no":
                    bh_no,

                    "depth":
                    depth,

                    "gwt":
                    gwt,

                    "location":
                    location,

                    "first_sample_depth":
                    first_sample_depth,

                    "first_sample_type":
                    first_sample_type

                })
                .execute()

            )

            borehole_id = (
                response.data[0]["id"]
            )

            generate_sample_log(

                borehole_id,

                depth,

                first_sample_depth,

                first_sample_type

            )

            st.success(
                "Borehole Created"
            )

            st.rerun()

