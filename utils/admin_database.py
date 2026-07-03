import streamlit as st
from supabase import create_client

admin_supabase = create_client(

    st.secrets["SUPABASE_URL"],

    st.secrets[
        "SUPABASE_SERVICE_ROLE_KEY"
    ]

)