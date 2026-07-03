import streamlit as st
import pandas as pd

from utils.auth import (
    require_admin
)

from utils.database import (
    supabase
)

require_admin()

if "summary_project" not in st.session_state:

    st.error(
        "No Project Selected"
    )

    st.stop()

project_id = st.session_state[
    "summary_project"
]

project = (

    supabase
    .table("projects")
    .select("*")
    .eq(
        "id",
        project_id
    )
    .single()
    .execute()

).data

st.title(
    f"Summary - {project['project_name']}"
)

if st.button(
    "⬅ Back"
):

    st.switch_page(
        "pages/02_Project.py"
    )

st.divider()

# =====================================
# LOAD BOREHOLES
# =====================================

boreholes = (

    supabase
    .table("boreholes")
    .select("*")
    .eq(
        "project_id",
        project_id
    )
    .order(
        "bh_no"
    )
    .execute()

).data

# =====================================
# LOAD SAMPLES
# =====================================

borehole_ids = [

    bh["id"]

    for bh in boreholes

]

samples = (

    supabase
    .table(
        "borehole_samples"
    )
    .select("*")
    .in_(
        "borehole_id",
        borehole_ids
    )
    .execute()

).data
gsa_submissions = (

    supabase
    .table(
        "gsa_submissions"
    )
    .select("*")
    .eq(
        "project_id",
        project_id
    )
    .execute()

).data
gsa_lookup = {

    (

        g["borehole_id"],

        float(g["depth"])

    ): g

    for g in gsa_submissions

}
# =====================================
# LOAD SG TESTS
# =====================================

sg_tests = (

    supabase
    .table(
        "specific_gravity_tests"
    )
    .select("*")
    .eq(
        "project_id",
        project_id
    )
    .execute()

).data
sg_lookup = {}

for row in sg_tests:

    key = (

        row["borehole_id"],

        float(row["depth"])

    )

    if key not in sg_lookup:

        sg_lookup[key] = []

    sg_lookup[key].append(row)
borehole_lookup = {

    bh["id"]: bh

    for bh in boreholes

}
# =====================================
# BUILD SUMMARY
# =====================================

summary_rows = []

for sample in samples:

    bh = borehole_lookup.get(

    sample["borehole_id"]

)

    if not bh:

        continue

    bh_name = (

        bh["bh_name"]

        if bh.get("bh_name")

        else bh["bh_no"]

    )

    # =========================
    # SPECIFIC GRAVITY
    # =========================

    sg_rows = sg_lookup.get(

    (

        sample["borehole_id"],

        float(sample["depth"])

    ),

    []

)

    sg_values = [

        r["specific_gravity"]

        for r in sg_rows

        if r.get(
            "specific_gravity"
        )

        is not None

    ]

    avg_sg = (

        round(

            sum(sg_values)

            /

            len(sg_values),

            3

        )

        if sg_values

        else None

    )

    # =========================
    # GSA
    # =========================

    gsa = gsa_lookup.get(

    (

        sample["borehole_id"],

        float(sample["depth"])

    )

)

    # =========================
    # STATUS
    # =========================

    statuses = [

        r.get(
            "approval_status"
        )

        for r in sg_rows

    ]

    if not statuses:

        status = "Not Started"

    elif any(

        s == "Returned"

        for s in statuses

    ):

        status = "Returned"

    elif all(

        s == "Approved"

        for s in statuses

    ):

        status = "Approved"

    else:

        status = "Pending"

    # =========================
    # SUMMARY ROW
    # =========================

    summary_rows.append({

        "Sample ID":
        sample.get(
            "sample_id"
        ),

        "Borehole":
        bh_name,

        "Depth":
        sample["depth"],

        "Type":
        sample["sample_type"],

        "SPT-N":
        sample.get(
            "spt_n_value"
        ),

        "Bulk Density":
        sample.get(
            "bulk_density"
        ),

        "Dry Unit Wt":
        sample.get(
            "dry_unit_weight"
        ),

        "Water Content":
        sample.get(
            "insitu_water_content"
        ),

        "Gravel %":
        (
            gsa.get(
                "gravel_percent"
            )
            if gsa
            else None
        ),

        "Sand %":
        (
            gsa.get(
                "sand_percent"
            )
            if gsa
            else None
        ),

        "Silt + Clay %":
        (
            gsa.get(
                "silt_clay_percent"
            )
            if gsa
            else None
        ),

        "Specific Gravity":
        avg_sg,

        "Status":
        status,

        "Remarks":
        sample.get(
            "remarks"
        )

    })
# =====================================
# DISPLAY
# =====================================

st.subheader(
    "Project Summary"
)

if summary_rows:

    df = pd.DataFrame(
        summary_rows
    )

    st.dataframe(

        df,

        use_container_width=True,

        hide_index=True

    )

else:

    st.info(
        "No Sample Data Found"
    )