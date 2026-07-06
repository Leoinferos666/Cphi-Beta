import streamlit as st
from utils.auth import login

st.set_page_config(
    page_title="C-Phi Login",
    layout="centered"
)

st.title(
    "C-Phi Laboratory"
)

st.subheader(
    "Login"
)

email = st.text_input(
    "Email"
)

password = st.text_input(
    "Password",
    type="password"
)

if st.button(
    "Login",
    use_container_width=True
):

    response = login(
        email,
        password
    )

    if response:

        st.success(
            "Login Successful"
        )

        st.switch_page(
            "pages/01_Dashboard.py"
        )
