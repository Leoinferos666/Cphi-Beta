import streamlit as st

from utils.database import supabase


def render():

    borehole_id = st.session_state[
        "selected_borehole"
    ]

    samples = (

        supabase
        .table(
            "borehole_samples"
        )
        .select("*")
        .eq(
            "borehole_id",
            borehole_id
        )
        .order(
            "depth"
        )
        .execute()

    ).data

    st.title(
        "Grain Size Analysis"
    )

    for sample in samples:

        c1, c2 = st.columns(
            [4,1]
        )

        with c1:

            st.write(

                f"{sample['sample_id']}"

                f" | "

                f"{sample['depth']} m"

                f" | "

                f"{sample['sample_type']}"

            )

        with c2:

            if st.button(

                "Open",

                key=sample["id"]

            ):

                st.session_state[
                    "selected_gsa_sample"
                ] = sample

                st.session_state[
                    "selected_test_subpage"
                ] = "gsa_entry"

                st.rerun()