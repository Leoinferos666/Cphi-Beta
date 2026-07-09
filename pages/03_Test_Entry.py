import streamlit as st

from utils.ui import apply_theme
from tests.liquid_limit.sample_selection import render
from tests.direct_shear.sample_selection import render as render_ds
from tests.rock_density_porosity.sample_selection import render as render_rdp
from tests.point_load.entry import render as render_point_load

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
# st.write("Selected Test:", selected_test)
# st.write("Selected Subpage:", selected_subpage)

# =====================================
# SPECIFIC GRAVITY DEPTH PAGE
# =====================================


if selected_subpage == "sg_depth":

    from tests.specific_gravity.depth import render

    render()
        
# =====================================
# POINT LOAD
# =====================================  
elif selected_subpage == "point_load":
    from tests.point_load.entry import render
    render()
    st.stop()
    
elif selected_subpage == "ucs":

    from tests.ucs.entry import render

    render()

    st.stop()

elif selected_subpage == "ll":

    from tests.liquid_limit.entry import render

    render()

    st.stop()
elif selected_test == "Liquid Limit":

    st.success("Reached Liquid Limit routing")

    
    render()

    st.stop()
elif selected_subpage == "ds":
    from tests.direct_shear.entry import render
    render()
    st.stop()
elif selected_subpage == "rdp":
    from tests.rock_density_porosity.entry import render
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
    
elif selected_subpage == "pl":

    from tests.plastic_limit.entry import render

    render()

    st.stop()

elif selected_test == "Plastic Limit":

    from tests.plastic_limit.sample_selection import render

    render()

    st.stop()
elif selected_test == "Direct Shear Test":
    render_ds()
elif selected_test == "Rock Density & Porosity":
    render_rdp()
elif selected_test == "Point Load Strength Index":
    render_point_load()
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