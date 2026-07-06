import streamlit as st

from utils.auth import (
    require_admin
)

from utils.database import get_supabase

supabase = get_supabase()
from utils.admin_database import (
    admin_supabase
)

# =====================================
# PAGE CONFIG
# =====================================

st.set_page_config(
    page_title="User Management",
    layout="wide"
)

require_admin()

# =====================================
# HEADER
# =====================================

col1, col2 = st.columns([1, 6])

with col1:

    if st.button(
        "🏠 Home"
    ):

        st.switch_page(
            "pages/01_Dashboard.py"
        )

with col2:

    st.title(
        "User Management"
    )

st.divider()

# =====================================
# CREATE USER
# =====================================

with st.expander(
    "➕ Create User",
    expanded=False
):

    with st.form(
        "create_user_form"
    ):

        full_name = st.text_input(
            "Full Name"
        )

        email = st.text_input(
            "Email"
        )

        password = st.text_input(
            "Password",
            type="password"
        )

        role = st.selectbox(

            "Role",

            [
                "Technician",
                "Admin"
            ]

        )

        create_user = (
            st.form_submit_button(
                "Create User"
            )
        )

        if create_user:

            if (
                not full_name
                or not email
                or not password
            ):

                st.error(
                    "All fields are required"
                )

            else:

                try:

                    auth_user = (
                        admin_supabase
                        .auth
                        .admin
                        .create_user({

                            "email":
                            email,

                            "password":
                            password,

                            "email_confirm":
                            True

                        })
                    )

                    user_id = (
                        auth_user.user.id
                    )

                    (
                        supabase
                        .table("users")
                        .insert({

                            "id":
                            user_id,

                            "email":
                            email,

                            "full_name":
                            full_name,

                            "role":
                            role,

                            "is_active":
                            True

                        })
                        .execute()
                    )

                    st.success(
                        "User Created Successfully"
                    )

                    st.rerun()

                except Exception as e:

                    st.error(str(e))

# =====================================
# USER LIST
# =====================================

st.divider()

st.subheader(
    "Existing Users"
)

users = (
    supabase
    .table("users")
    .select("*")
    .order(
        "created_at",
        desc=True
    )
    .execute()
)

if not users.data:

    st.info(
        "No Users Found"
    )

else:

    for user in users.data:

        with st.container(
            border=True
        ):

            c1, c2, c3, c4 = st.columns(
                [3, 2, 2, 1]
            )

            # =====================
            # USER DETAILS
            # =====================

            with c1:

                st.write(
                    f"### {user['full_name']}"
                )

                st.caption(
                    user["email"]
                )

            # =====================
            # ROLE
            # =====================

            with c2:

                role_options = [
                    "Admin",
                    "Technician"
                ]

                current_index = (
                    0
                    if user["role"]
                    == "Admin"
                    else 1
                )

                new_role = st.selectbox(

                    "Role",

                    role_options,

                    index=current_index,

                    key=f"role_{user['id']}"

                )

            # =====================
            # ACTIVE
            # =====================

            with c3:

                active = st.checkbox(

                    "Active",

                    value=user.get(
                        "is_active",
                        True
                    ),

                    key=f"active_{user['id']}"

                )

            # =====================
            # SAVE
            # =====================

            with c4:

                st.write("")
                st.write("")

                if st.button(

                    "Save",

                    key=f"save_{user['id']}",

                    use_container_width=True

                ):

                    try:

                        (
                            supabase
                            .table("users")
                            .update({

                                "role":
                                new_role,

                                "is_active":
                                active

                            })
                            .eq(
                                "id",
                                user["id"]
                            )
                            .execute()
                        )

                        st.success(
                            "User Updated"
                        )

                        st.rerun()

                    except Exception as e:

                        st.error(str(e))