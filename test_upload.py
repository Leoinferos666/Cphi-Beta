import streamlit as st

from utils.storage import (
    upload_file
)

file = st.file_uploader(
    "Upload"
)

if file:

    url = upload_file(file)

    st.write(url)