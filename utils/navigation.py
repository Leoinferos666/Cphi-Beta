import streamlit as st

def show_home_button():

    col1, col2 = st.columns([1, 8])

    with col1:

        if st.button(
            "🏠 Home",
            use_container_width=True
        ):

            st.switch_page(
                "pages/01_Dashboard.py"
            )

    st.divider()