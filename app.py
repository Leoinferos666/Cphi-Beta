import streamlit as st

st.set_page_config(
    page_title="C-Phi",
    layout="wide"
)

st.switch_page(
    "pages/00_Login.py"
)

#ngrok http 8501 ngrok http 8501 --basic-auth="client:demo1234"