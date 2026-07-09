import streamlit as st
import pandas as pd

from utils.auth import (
    require_admin
)

from utils.database import get_supabase

supabase = get_supabase()
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
# st.write("Project ID:", project_id)
# st.write("Boreholes:", len(boreholes))
# st.write("Borehole IDs:", borehole_ids)
# st.write("Samples:", len(samples))
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
# LOAD LIQUID LIMIT
# =====================================

ll_submissions = (
    supabase
    .table("ll_submissions")
    .select("*")
    .eq("project_id", project_id)
    .execute()
).data

ll_lookup = {
    (
        row["borehole_id"],
        row["sample_id"]
    ): row
    for row in ll_submissions
}
# =====================================
# LOAD PLASTIC LIMIT
# =====================================

pl_submissions = (
    supabase
    .table("pl_submissions")
    .select("*")
    .eq("project_id", project_id)
    .execute()
).data

pl_lookup = {
    (
        row["borehole_id"],
        row["sample_id"]
    ): row
    for row in pl_submissions
}   
# =====================================
# LOAD DIRECT SHEAR
# =====================================

ds_submissions = (
    supabase
    .table("ds_submissions")
    .select("*")
    .eq("project_id", project_id)
    .execute()
).data

ds_lookup = {
    (
        row["borehole_id"],
        row["sample_id"]
    ): row
    for row in ds_submissions
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
# LOAD SG DEPTHS
# =====================================
sg_submissions = (
        supabase
        .table("specific_gravity_submissions")
        .select("*")
        .eq("project_id", project_id)
        .execute()
    ).data

submission_lookup = {
        row["id"]: row
        for row in sg_submissions
    }

sg_depths = (
    supabase
    .table("specific_gravity_depths")
    .select("*")
    .execute()
).data

sg_depth_lookup = {}

for row in sg_depths:

    submission = submission_lookup.get(row["submission_id"])

    if submission is None:
        continue

    sg_depth_lookup[
        (
            submission["borehole_id"],
            row["sample_id"]
        )
    ] = row
  
# =====================================
# BUILD SUMMARY
# =====================================

summary_rows = []

for sample in samples:
    # st.write(sample["sample_id"])
    # st.write("Appending...")
    # st.write("Loop:", sample["sample_id"])
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
          
    # =====================================
    # LOAD ROCK DENSITY & POROSITY
    # =====================================

    rdp_submissions = (
        supabase
        .table("rock_density_porosity_submissions")
        .select("*")
        .eq("project_id", project_id)
        .execute()
    ).data
    rdp_observations = (
        supabase
        .table("rock_density_porosity_observations")
        .select("*")
        .execute()
    ).data
    rdp_lookup = {}

    for obs in rdp_observations:

        submission = next(
            (
                s for s in rdp_submissions
                if s["id"] == obs["submission_id"]
            ),
            None
        )

        if submission:

            rdp_lookup[
                (
                    submission["borehole_id"],
                    submission["sample_id"]
                )
            ] = obs

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

        else "-"

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
    # LIQUID LIMIT
    # =========================

    ll = ll_lookup.get(
        (
            sample["borehole_id"],
            sample["sample_id"]
        )
    )

    # =========================
    # PLASTIC LIMIT
    # =========================

    pl = pl_lookup.get(
        (
            sample["borehole_id"],
            sample["sample_id"]
        )
    )
    # =========================
    # DIRECT SHEAR
    # =========================

    ds = ds_lookup.get(
        (
            sample["borehole_id"],
            sample["sample_id"]
        )
    )
    rdp = rdp_lookup.get(
        (
            sample["borehole_id"],
            sample["sample_id"]
        )
    )
    pi = None

    if (
        ll
        and pl
        and ll.get("liquid_limit") is not None
        and pl.get("plastic_limit") is not None
    ):
        pi = round(
            ll["liquid_limit"] - pl["plastic_limit"],
            2
        )
  
    # =========================
    # STATUS
    # =========================

    statuses = [
        r.get("approval_status")
        for r in sg_rows
    ]

    if not statuses:
        status = "Not Started"

    elif any(s == "Returned" for s in statuses):
        status = "Returned"

    elif all(s == "Approved" for s in statuses):
        status = "Approved"

    else:
        status = "Pending"
    sg_depth = sg_depth_lookup.get(
    (
        sample["borehole_id"],
        sample["sample_id"]
    ),
    {}
)
    summary_rows.append({
        "Sample_DB_ID": sample["id"],
        "Sample ID": sample.get("sample_id"),
        "Borehole": bh_name,
        "Depth": sample["depth"],
        # "Sample Type": sample.get("sample_type", "Soil"),
        "Sample Type": sample["sample_type"],

            "Material": sg_depth.get(
                "material_type",
                "Soil"
            ),

            "Rock Number": sg_depth.get(
                "rock_number"
            ),

        "SPT-N": sample.get("spt_n_value"),
        "Bulk Density": sample.get("bulk_density"),
        "Dry Unit Wt": sample.get("dry_unit_weight"),
        "Water Content": sample.get("insitu_water_content"),

        "Gravel %": gsa.get("gravel_percent") if gsa else "-",
        "Sand %": gsa.get("sand_percent") if gsa else "-",
        "Silt + Clay %": gsa.get("silt_clay_percent") if gsa else "-",

        "Specific Gravity": avg_sg,

        "Liquid Limit":
            round(ll["liquid_limit"], 2)
            if ll and ll.get("liquid_limit") is not None
            else "-",

        "Plastic Limit":
            round(pl["plastic_limit"], 2)
            if pl and pl.get("plastic_limit") is not None
            else "-",

        "Plasticity Index": pi,
        "Cohesion,c (kg/cm²)":
            round(ds["cohesion"], 3)
            if ds and ds.get("cohesion") is not None
            else "-",

        "Internal Friction Angle, φ (°)":   
            round(ds["phi"], 2)
            if ds and ds.get("phi") is not None
            else "-",
            "Rock Density":
        round(rdp["density"], 3)
        if rdp and rdp.get("density") is not None
        else "-",

    "Rock Porosity (%)":
        round(rdp["porosity"], 2)
        if rdp and rdp.get("porosity") is not None
        else "-",

        # "Status": status,
        # "Remarks": sample.get("remarks")

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

    edited_df = st.data_editor(

        df,

        use_container_width=True,

        hide_index=True,
        column_config={
            "Sample_DB_ID": None
        },

        disabled=[

            "Sample ID",
            "Borehole",
            "Depth",
            "Type",
            # "Water Content",
            "Gravel %",
            "Sand %",
            "Silt + Clay %",
            "Specific Gravity",
            "Liquid Limit",
            "Plastic Limit",
            "Plasticity Index",
            "Direct Shear c",
            "Direct Shear φ",
            "Status",
            "Remarks",
            "Rock Density",
            "Rock Porosity (%)",
        ]

    )
    if st.button(
        "💾 Save Summary Changes",
        use_container_width=True
    ):
        
        for _, row in edited_df.iterrows():

            (
                supabase
                .table("borehole_samples")
                .update({

                    "spt_n_value": row["SPT-N"],

                    "bulk_density": row["Bulk Density"],

                    "dry_unit_weight": row["Dry Unit Wt"]

                })
                .eq("sample_id", row["Sample_DB_ID"])
                .execute()
            )

        st.success("Summary updated successfully.")

        st.rerun()

else:

    st.info(
        "No Sample Data Found"
    )