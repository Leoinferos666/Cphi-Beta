import streamlit as st

from utils.auth import (
    is_admin
)

from utils.database import get_supabase

supabase = get_supabase()
from utils.sample_log import (
    get_sample_log,
    delete_sample_log,
    generate_sample_log
)

from components.sample_log_editor import (
    render as render_sample_log
)


def render(
    bh,
    samples
):

    

    setup_required = (

        bh["depth"] == 0

        or

        bh["first_sample_depth"]
        is None

        or

        bh["first_sample_type"]
        is None

    )

    with st.container(
        border=True
    ):

        display_name = (

            bh["bh_name"]

            if bh.get("bh_name")

            else bh["bh_no"]

        )

        st.subheader(
            display_name
        )
        if is_admin():

            new_bh_name = st.text_input(

                "BH Name",

                value=bh.get(
                    "bh_name",
                    bh["bh_no"]
                ),

                key=f"name_{bh['id']}"

            )

            if st.button(

                "Save BH Name",

                key=f"save_name_{bh['id']}"

            ):

                (
                    supabase
                    .table(
                        "boreholes"
                    )
                    .update({

                        "bh_name":
                        new_bh_name

                    })
                    .eq(
                        "id",
                        bh["id"]
                    )
                    .execute()
                )

                st.success(
                    "BH Name Updated"
                )

                st.rerun()

        if setup_required:

            st.warning(
                "Setup Required"
            )

        else:

            st.success(
                "Ready"
            )

        st.write(
            f"Depth : {bh['depth']} m"
        )

        st.write(
            f"GWT : {bh['gwt']} m"
        )

        st.write(
            f"Location : {bh['location']}"
        )

        st.write(
            f"Samples : {len(samples)}"
        )

        # ==========================
        # SETUP BOREHOLE
        # ==========================

        if setup_required:

            with st.form(
                f"setup_{bh['id']}"
            ):

                depth = st.number_input(
                    "Depth (m)",
                    value=20.0,
                    key=f"d_{bh['id']}"
                )

                gwt = st.number_input(
                    "GWT (m)",
                    value=0.0,
                    key=f"g_{bh['id']}"
                )

                location = st.text_input(
                    "Location",
                    key=f"l_{bh['id']}"
                )

                first_sample_depth = (
                    st.number_input(

                        "First Sample Depth",

                        value=1.5,

                        step=0.5,

                        key=f"fsd_{bh['id']}"

                    )
                )

                first_sample_type = (
                    st.selectbox(

                        "First Sample Type",

                        [
                            "SPT",
                            "UDS",
                            "CORE"
                        ],

                        key=f"fst_{bh['id']}"

                    )
                )

                save = (
                    st.form_submit_button(
                        "Generate Sample Log"
                    )
                )

                if save:

                    (
                        supabase
                        .table(
                            "boreholes"
                        )
                        .update({

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
                        .eq(
                            "id",
                            bh["id"]
                        )
                        .execute()
                    )

                    generate_sample_log(

                        bh["id"],

                        depth,

                        first_sample_depth,

                        first_sample_type

                    )

                    st.rerun()

            return

        # ==========================
        # NORMAL CARD
        # ==========================

        c1, c2, c3 = st.columns(
            3
        )

        with c1:

            if st.button(
                "Select",
                key=f"select_{bh['id']}"
            ):

                st.session_state[
                    "selected_borehole"
                ] = bh["id"]

                st.rerun()

        with c2:

            if st.button(
                "Sample Log",
                key=f"log_{bh['id']}"
            ):

                st.session_state[
                    "sample_log"
                ] = bh["id"]

                st.rerun()

        with c3:

            if is_admin():

                if st.button(
                    "Delete",
                    key=f"delete_{bh['id']}"
                ):

                    (
                        supabase
                        .table(
                            "boreholes"
                        )
                        .delete()
                        .eq(
                            "id",
                            bh["id"]
                        )
                        .execute()
                    )

                    st.rerun()

        if (
            st.session_state.get(
                "sample_log"
            )
            == bh["id"]
        ):

            st.divider()

            render_sample_log(
                bh,
                samples
            )
