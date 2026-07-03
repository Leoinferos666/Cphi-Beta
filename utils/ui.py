import streamlit as st

def apply_theme():

    st.markdown(
        """
        <style>

        .block-container {
            max-width: 1200px;
            padding-top: 5rem;
            padding-bottom: 2rem;
        }

        div[data-testid="stHorizontalBlock"]{
            gap:0.5rem;
        }

        button[kind="primary"]{
            width:100%;
        }

        @media (max-width: 768px){

            .block-container{
                padding-left:1rem;
                padding-right:1rem;
            }

        }

        </style>
        """,
        unsafe_allow_html=True
    )