import streamlit as st
from utils.database import supabase


def render(
    project_id,
    borehole_id,
    test_name,
    depth=None
):

    st.subheader(
        "Attachments"
    )

    # ============================
    # LOAD REQUIREMENTS
    # ============================

    config = (
        supabase
        .table("project_tests")
        .select("*")
        .eq(
            "project_id",
            project_id
        )
        .eq(
            "test_name",
            test_name
        )
        .execute()
    )

    image_required = False
    graph_required = False

    if config.data:

        image_required = (
            config.data[0]
            .get(
                "image_requirement",
                "Optional"
            )
            == "Required"
        )

        graph_required = (
            config.data[0]
            .get(
                "graph_requirement",
                "Optional"
            )
            == "Required"
        )

    # ============================
    # IMAGE UPLOAD
    # ============================

    st.write("### Images")

    if image_required:

        st.warning(
            "Images Required"
        )

    image_file = st.file_uploader(

        "Upload Image",

        type=[
            "jpg",
            "jpeg",
            "png"
        ],

        key=f"img_{test_name}_{depth}"

    )

    if image_file:

        st.success(
            image_file.name
        )

    # ============================
    # GRAPH UPLOAD
    # ============================

    st.write("### Graphs")

    if graph_required:

        st.warning(
            "Graphs Required"
        )

    graph_file = st.file_uploader(

        "Upload Graph",

        type=[
            "jpg",
            "jpeg",
            "png",
            "pdf"
        ],

        key=f"graph_{test_name}_{depth}"

    )

    if graph_file:

        st.success(
            graph_file.name
        )

    # ============================
    # SAVE
    # ============================

    if st.button(
        "Save Attachments",
        key=f"attach_{test_name}_{depth}"
    ):

        if image_file:

            (
                supabase
                .table(
                    "test_attachments"
                )
                .insert({

                    "project_id":
                    project_id,

                    "borehole_id":
                    borehole_id,

                    "test_name":
                    test_name,

                    "depth":
                    depth,

                    "file_type":
                    "Image",

                    "file_url":
                    image_file.name

                })
                .execute()
            )

        if graph_file:

            (
                supabase
                .table(
                    "test_attachments"
                )
                .insert({

                    "project_id":
                    project_id,

                    "borehole_id":
                    borehole_id,

                    "test_name":
                    test_name,

                    "depth":
                    depth,

                    "file_type":
                    "Graph",

                    "file_url":
                    graph_file.name

                })
                .execute()
            )

        st.success(
            "Attachments Saved"
        )

        st.rerun()

    # ============================
    # EXISTING FILES
    # ============================

    attachments = (
        supabase
        .table(
            "test_attachments"
        )
        .select("*")
        .eq(
            "project_id",
            project_id
        )
        .eq(
            "borehole_id",
            borehole_id
        )
        .eq(
            "test_name",
            test_name
        )
        .execute()
    )

    if attachments.data:

        st.divider()

        st.write(
            "### Uploaded Files"
        )

        for file in attachments.data:

            st.write(

                f"{file['file_type']} - "

                f"{file['file_url']}"

            )