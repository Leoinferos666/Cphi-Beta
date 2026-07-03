import streamlit as st

def back_to_project():

    if st.button("⬅ Project"):

        st.session_state.pop(
            "selected_test_subpage",
            None
        )

        st.switch_page(
            "pages/02_Project.py"
        )