import streamlit as st


def render(
    project,
    borehole_count,
    is_admin=False
):
    """
    Returns:
        "open"
        "delete"
        None
    """

    action = None

    with st.container(border=True):

        st.subheader(project["project_name"])

        st.caption(
            project.get("client_name", "-")
        )

        st.write(
            project.get("location", "-")
        )

        st.write(
            f"**Boreholes:** {borehole_count}"
        )

        st.write("")

        c1, c2 = st.columns(2)

        with c1:

            if st.button(
                "Open",
                key=f"open_{project['id']}",
                use_container_width=True
            ):

                action = "open"

        with c2:

            if is_admin:

                if st.button(
                    "Delete",
                    key=f"delete_{project['id']}",
                    use_container_width=True
                ):

                    action = "delete"

    return action