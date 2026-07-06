import streamlit as st
from utils.database import supabase


def login(email, password):

    try:

        response = (
            supabase.auth.sign_in_with_password({

                "email": email,
                "password": password

            })
        )

        return response

    except Exception as e:

        st.error(str(e))
        return None


def logout():

    try:

        supabase.auth.sign_out()

    except:
        pass

    for key in list(
        st.session_state.keys()
    ):

        del st.session_state[key]

def get_current_user():

    return st.session_state.get("user")

def load_user_profile():

    user = (
        get_current_user()
    )

    if not user:

        return None

    profile = (

        supabase
        .table("users")
        .select("*")
        .eq(
            "id",
            user.id
        )
        .execute()

    )

    if not profile.data:

        return None

    profile = profile.data[0]

    if not profile.get(
        "is_active",
        True
    ):

        logout()

        st.error(
            "Account Disabled"
        )

        st.stop()

    return profile


def get_role():

    profile = (
        load_user_profile()
    )

    if not profile:

        return None

    return profile.get(
        "role"
    )


def get_user_name():

    profile = (
        load_user_profile()
    )

    if not profile:

        return ""

    return profile.get(
        "full_name",
        ""
    )


def is_admin():

    role = (
        get_role()
    )

    return role == "Admin"


def is_technician():

    role = (
        get_role()
    )

    return role == "Technician"


def require_login():

    user = (
        get_current_user()
    )

    if not user:

        st.switch_page(
            "pages/00_Login.py"
        )

        st.stop()


def require_admin():

    require_login()

    if not is_admin():

        st.error(
            "Access Denied"
        )

        st.stop()


def require_technician():

    require_login()

    if not is_technician():

        st.error(
            "Access Denied"
        )

        st.stop()