import streamlit as st

from utils.ui import apply_theme

st.set_page_config(
    page_title="...",
    layout="wide"
)

apply_theme()

selected_test = st.session_state.get(
    "selected_test"
)

selected_subpage = st.session_state.get(
    "selected_test_subpage"
)

# =====================================
# SPECIFIC GRAVITY DEPTH PAGE
# =====================================

if selected_subpage == "sg_depth":

    from tests.specific_gravity.depth import render

    render()
    

elif selected_subpage == "ll":

    from tests.liquid_limit.entry import render

    render()

    st.stop()
elif selected_test == "Liquid Limit":

    st.success("Reached Liquid Limit routing")

    from tests.liquid_limit.sample_selection import render

    render()

    st.stop()
# =====================================
# GSA ENTRY PAGE
# =====================================

elif selected_subpage == "gsa_entry":

    from tests.gsa.entry import render

    render()

# =====================================
# SPECIFIC GRAVITY MAIN PAGE
# =====================================

elif selected_test == "Specific Gravity":

    from tests.specific_gravity.entry import render

    render()

# =====================================
# GSA MAIN PAGE
# =====================================

elif selected_test == "Grain Size Analysis":

    from tests.gsa.sample_selection import render

    render()

# =====================================
# FUTURE TESTS
# =====================================

elif selected_test == "Moisture Content":

    st.info(
        "Moisture Content Coming Soon"
    )

elif selected_test == "Liquid Limit":

    st.info(
        "Liquid Limit Coming Soon"
    )

else:

    st.warning(
        "No Test Selected"
    )