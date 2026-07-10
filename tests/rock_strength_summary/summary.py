import streamlit as st
from utils.database import get_supabase

supabase = get_supabase()


def render():

    if "selected_project" not in st.session_state:
        st.error("No Project Selected")
        st.stop()

    if "selected_borehole" not in st.session_state:
        st.error("No Borehole Selected")
        st.stop()

    project_id = st.session_state["selected_project"]
    borehole_id = st.session_state["selected_borehole"]

    st.title("Rock Strength Summary")

    st.divider()