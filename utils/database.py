from supabase import create_client
import streamlit as st


def get_supabase():

    if "supabase_client" not in st.session_state:

        st.session_state["supabase_client"] = create_client(
            st.secrets["SUPABASE_URL"],
            st.secrets["SUPABASE_KEY"]
        )

    return st.session_state["supabase_client"]