# import streamlit as st
# import pandas as pd

# from utils.auth import (
#     require_admin
# )

# from utils.database import get_supabase

# supabase = get_supabase()
# require_admin()

# if "summary_project" not in st.session_state:

#     st.error(
#         "No Project Selected"
#     )

#     st.stop()

# project_id = st.session_state[
#     "summary_project"
# ]

# project = (

#     supabase
#     .table("projects")
#     .select("*")
#     .eq(
#         "id",
#         project_id
#     )
#     .single()
#     .execute()

# ).data

# st.title(
#     f"Summary - {project['project_name']}"
# )

# if st.button(
#     "⬅ Back"
# ):

#     st.switch_page(
#         "pages/02_Project.py"
#     )

# st.divider()

# # =====================================
# # LOAD BOREHOLES
# # =====================================

# boreholes = (

#     supabase
#     .table("boreholes")
#     .select("*")
#     .eq(
#         "project_id",
#         project_id
#     )
#     .order(
#         "bh_no"
#     )
#     .execute()

# ).data

# # =====================================
# # LOAD SAMPLES
# # =====================================

# borehole_ids = [

#     bh["id"]

#     for bh in boreholes

# ]

# samples = (

#     supabase
#     .table(
#         "borehole_samples"
#     )
#     .select("*")
#     .in_(
#         "borehole_id",
#         borehole_ids
#     )
#     .execute()

# ).data
# # st.write("Project ID:", project_id)
# # st.write("Borehole IDs:", borehole_ids)
# # st.write("Samples:", samples)
# # st.write("Project ID:", project_id)
# # st.write("Boreholes:", len(boreholes))
# # st.write("Borehole IDs:", borehole_ids)
# # st.write("Samples:", len(samples))
# gsa_submissions = (

#     supabase
#     .table(
#         "gsa_submissions"
#     )
#     .select("*")
#     .eq(
#         "project_id",
#         project_id
#     )
#     .execute()

# ).data
# gsa_lookup = {

#     (

#         g["borehole_id"],

#         float(g["depth"])

#     ): g

#     for g in gsa_submissions

# }
# # =====================================
# # LOAD LIQUID LIMIT
# # =====================================

# ll_submissions = (
#     supabase
#     .table("ll_submissions")
#     .select("*")
#     .eq("project_id", project_id)
#     .execute()
# ).data

# ll_lookup = {
#     (
#         row["borehole_id"],
#         row["sample_id"]
#     ): row
#     for row in ll_submissions
# }
# # =====================================
# # LOAD PLASTIC LIMIT
# # =====================================

# pl_submissions = (
#     supabase
#     .table("pl_submissions")
#     .select("*")
#     .eq("project_id", project_id)
#     .execute()
# ).data

# pl_lookup = {
#     (
#         row["borehole_id"],
#         row["sample_id"]
#     ): row
#     for row in pl_submissions
# }   
# # st.write("PL Submissions")
# # st.write(pl_submissions)

# # st.write("PL Lookup")
# # st.write(pl_lookup) 
# # # =====================================
# # LOAD DIRECT SHEAR
# # =====================================

# ds_submissions = (
#     supabase
#     .table("ds_submissions")
#     .select("*")
#     .eq("project_id", project_id)
#     .execute()
# ).data

# ds_lookup = {
#     (
#         row["borehole_id"],
#         row["sample_id"]
#     ): row
#     for row in ds_submissions
# }

# # =====================================
# # LOAD SG TESTS
# # =====================================


# sg_tests = (

#     supabase
#     .table(
#         "specific_gravity_tests"
#     )
#     .select("*")
#     .eq(
#         "project_id",
#         project_id
#     )
#     .execute()

# ).data
# sg_lookup = {}

# for row in sg_tests:

#     key = (

#         row["borehole_id"],

#         float(row["depth"])

#     )

#     if key not in sg_lookup:

#         sg_lookup[key] = []

#     sg_lookup[key].append(row)
# borehole_lookup = {

#     bh["id"]: bh

#     for bh in boreholes

# }
# # =====================================
# # LOAD SG DEPTHS
# # =====================================
# sg_submissions = (
#         supabase
#         .table("specific_gravity_submissions")
#         .select("*")
#         .eq("project_id", project_id)
#         .execute()
#     ).data

# submission_lookup = {
#         row["id"]: row
#         for row in sg_submissions
#     }

# sg_depths = (
#     supabase
#     .table("specific_gravity_depths")
#     .select("*")
#     .execute()
# ).data

# sg_depth_lookup = {}

# for row in sg_depths:

#     submission = submission_lookup.get(row["submission_id"])

#     if submission is None:
#         continue

#     sg_depth_lookup[
#         (
#             submission["borehole_id"],
#             row["sample_id"]
#         )
#     ] = row
  
# # =====================================
# # BUILD SUMMARY
# # =====================================

# summary_rows = []

# for sample in samples:
#     # st.write(sample["sample_id"])
#     # st.write("Appending...")
#     # st.write("Loop:", sample["sample_id"])
#     bh = borehole_lookup.get(

#     sample["borehole_id"]

# )

#     if not bh:

#         continue

#     bh_name = (

#         bh["bh_name"]

#         if bh.get("bh_name")

#         else bh["bh_no"]

#     )
          
#     # =====================================
#     # LOAD ROCK DENSITY & POROSITY
#     # =====================================

#     rdp_submissions = (
#         supabase
#         .table("rock_density_porosity_submissions")
#         .select("*")
#         .eq("project_id", project_id)
#         .execute()
#     ).data
#     rdp_observations = (
#         supabase
#         .table("rock_density_porosity_observations")
#         .select("*")
#         .execute()
#     ).data
#     rdp_lookup = {}

#     for obs in rdp_observations:

#         submission = next(
#             (
#                 s for s in rdp_submissions
#                 if s["id"] == obs["submission_id"]
#             ),
#             None
#         )

#         if submission:

#             rdp_lookup[
#                 (
#                     submission["borehole_id"],
#                     submission["sample_id"]
#                 )
#             ] = obs

#     # =========================
#     # SPECIFIC GRAVITY
#     # =========================

#     sg_rows = sg_lookup.get(

#     (

#         sample["borehole_id"],

#         float(sample["depth"])

#     ),

#     []

# )

#     sg_values = [

#         r["specific_gravity"]

#         for r in sg_rows

#         if r.get(
#             "specific_gravity"
#         )

#         is not None

#     ]

#     avg_sg = (

#         round(

#             sum(sg_values)

#             /

#             len(sg_values),

#             3

#         )

#         if sg_values

#         else "-"

#     )

#     # =========================
#     # GSA
#     # =========================

#     gsa = gsa_lookup.get(

#     (

#         sample["borehole_id"],

#         float(sample["depth"])

#     )

# )

#     # =========================
#     # LIQUID LIMIT
#     # =========================

#     ll = ll_lookup.get(
#         (
#             sample["borehole_id"],
#             sample["sample_id"]
#         )
#     )

#     # =========================
#     # PLASTIC LIMIT
#     # =========================

#     pl = pl_lookup.get(
#         (
#             sample["borehole_id"],
#             sample["sample_id"]
#         )
#     )
#     # pl = pl_lookup.get(
#     #     (
#     #         sample["borehole_id"],
#     #         sample["sample_id"]
#     #     )
#     # )
#     # # =========================
#     # DIRECT SHEAR
#     # =========================

#     ds = ds_lookup.get(
#         (
#             sample["borehole_id"],
#             sample["sample_id"]
#         )
#     )
#     rdp = rdp_lookup.get(
#         (
#             sample["borehole_id"],
#             sample["sample_id"]
#         )
#     )
#     pi = None

#     if (
#         ll
#         and pl
#         and ll.get("liquid_limit") is not None
#         and pl.get("plastic_limit") is not None
#     ):
#         pi = round(
#             ll["liquid_limit"] - pl["plastic_limit"],
#             2
#         )
  
#     # =========================
#     # STATUS
#     # =========================

#     statuses = [
#         r.get("approval_status")
#         for r in sg_rows
#     ]

#     if not statuses:
#         status = "Not Started"

#     elif any(s == "Returned" for s in statuses):
#         status = "Returned"

#     elif all(s == "Approved" for s in statuses):
#         status = "Approved"

#     else:
#         status = "Pending"
#     sg_depth = sg_depth_lookup.get(
#     (
#         sample["borehole_id"],
#         sample["sample_id"]
#     ),
#     {}
# )
#     summary_rows.append({
#         "Sample_DB_ID": sample["id"],
#         "Sample ID": sample.get("sample_id"),
#         "Borehole": bh_name,
#         "Depth": sample["depth"],
#         # "Sample Type": sample.get("sample_type", "Soil"),
#         "Sample Type": sample["sample_type"],

#             "Material": sg_depth.get(
#                 "material_type",
#                 "Soil"
#             ),

#             "Rock Number": sg_depth.get(
#                 "rock_number"
#             ),

#         "SPT-N": sample.get("spt_n_value"),
#         "Bulk Density": sample.get("bulk_density"),
#         "Dry Unit Wt": sample.get("dry_unit_weight"),
#         "Water Content": sample.get("insitu_water_content"),

#         "Gravel %": gsa.get("gravel_percent") if gsa else "-",
#         "Sand %": gsa.get("sand_percent") if gsa else "-",
#         "Silt + Clay %": gsa.get("silt_clay_percent") if gsa else "-",

#         "Specific Gravity": avg_sg,

#         "Liquid Limit":
#             round(ll["liquid_limit"], 2)
#             if ll and ll.get("liquid_limit") is not None
#             else "-",

#         "Plastic Limit":
#             round(pl["plastic_limit"], 2)
#             if pl and pl.get("plastic_limit") is not None
#             else "-",

#         "Plasticity Index": pi,
#         "Cohesion,c (kg/cm²)":
#             round(ds["cohesion"], 3)
#             if ds and ds.get("cohesion") is not None
#             else "-",

#         "Internal Friction Angle, φ (°)":   
#             round(ds["phi"], 2)
#             if ds and ds.get("phi") is not None
#             else "-",
#             "Rock Density":
#         round(rdp["density"], 3)
#         if rdp and rdp.get("density") is not None
#         else "-",

#     "Rock Porosity (%)":
#         round(rdp["porosity"], 2)
#         if rdp and rdp.get("porosity") is not None
#         else "-",

#         # "Status": status,
#         # "Remarks": sample.get("remarks")

#     })

# # =====================================
# # DISPLAY
# # =====================================

# st.subheader(
#     "Project Summary"
# )

# if summary_rows:

#     df = pd.DataFrame(
#         summary_rows
#     )

#     edited_df = st.data_editor(

#         df,

#         use_container_width=True,

#         hide_index=True,
#         column_config={
#             "Sample_DB_ID": None
#         },

#         disabled=[

#             "Sample ID",
#             "Borehole",
#             "Depth",
#             "Type",
#             # "Water Content",
#             "Gravel %",
#             "Sand %",
#             "Silt + Clay %",
#             "Specific Gravity",
#             "Liquid Limit",
#             "Plastic Limit",
#             "Plasticity Index",
#             "Direct Shear c",
#             "Direct Shear φ",
#             "Status",
#             "Remarks",
#             "Rock Density",
#             "Rock Porosity (%)",
#         ]

#     )
#     if st.button(
#         "💾 Save Summary Changes",
#         use_container_width=True
#     ):
        
#         for _, row in edited_df.iterrows():

#             (
#                 supabase
#                 .table("borehole_samples")
#                 .update({

#                     "spt_n_value": row["SPT-N"],

#                     "bulk_density": row["Bulk Density"],

#                     "dry_unit_weight": row["Dry Unit Wt"]

#                 })
#                 .eq("sample_id", row["Sample_DB_ID"])
#                 .execute()
#             )

#         st.success("Summary updated successfully.")

#         st.rerun()

# else:

#     st.info(
#         "No Sample Data Found"
#     )
#     # =====================================
#     # ROCK STRENGTH SUMMARY
#     # =====================================

# st.divider()

# st.header("Rock Strength Summary")
# # =====================================
# # LOAD ROCK SUMMARY
# # =====================================

# rock_summary = (
#     supabase
#     .table("rock_strength_summary")
#     .select("*")
#     .eq("project_id", project_id)
#     .order("borehole_id")
#     .order("depth_from")
#     .execute()
# ).data

# # st.write("Existing Summary Rows:", len(rock_summary))
# # =====================================
# # LOAD APPROVED ROCK DENSITY SUBMISSIONS
# # =====================================

# rdp_submissions = (
#     supabase
#     .table("rock_density_porosity_submissions")
#     .select("*")
#     .eq("project_id", project_id)
#     .execute()
# ).data

# # st.write(rdp_submissions)
# # =====================================
# # LOAD ROCK SPECIMENS
# # =====================================

# rdp_specimens = (
#     supabase
#     .table("rock_density_porosity_observations")
#     .select("*")
#     .execute()
# ).data
# # =====================================
# # LOAD APPROVED POINT LOAD
# # =====================================

# pl_submissions = (
#     supabase
#     .table("point_load_submissions")
#     .select("*")
#     .eq("project_id", project_id)
#     .eq("review_status", "Approved")
#     .execute()
# ).data

# # st.write("Approved Point Load:", len(pl_submissions))
# # =====================================
# # LOAD POINT LOAD SPECIMENS
# # =====================================

# pl_specimens = (
#     supabase
#     .table("point_load_specimens")
#     .select("*")
#     .execute()
# ).data
# approved_pl_ids = {
#     row["id"]
#     for row in pl_submissions
# }

# pl_specimens = [
#     row
#     for row in pl_specimens
#     if row["submission_id"] in approved_pl_ids
# ]
# pl_submission_lookup = {
#     row["id"]: row
#     for row in pl_submissions
# }
# # st.write("Approved Point Load Specimens:", len(pl_specimens))
# # =====================================
# # CREATE SUMMARY ROWS FROM POINT LOAD
# # =====================================

# for specimen in pl_specimens:
#     submission = pl_submission_lookup[specimen["submission_id"]]
#     existing = (
#         supabase
#         .table("rock_strength_summary")
#         .select("id")
#         .eq("project_id", project_id)
#             .eq("borehole_id", submission["borehole_id"])
#             .eq("rock_number", specimen["rock_number"])
#             .execute()
#         ).data

#     if not existing:

#             (
#                 supabase
#                 .table("rock_strength_summary")
#                 .insert({

#                     "project_id": project_id,

#                     "borehole_id": submission["borehole_id"],

#                     "rock_number": specimen["rock_number"],

#                     "method_of_drilling": None,

#                     "depth_from": specimen["depth_from"],

#                     "depth_to": specimen["depth_to"],

#                     "rock_sample_type": None,

#                     "description": None,

#                     "cr_percent": None,

#                     "rqd_percent": None

#                 })
#                 .execute()
#             )
#             rock_summary = (
#         supabase
#         .table("rock_strength_summary")
#         .select("*")
#         .eq("project_id", project_id)
#         .order("depth_from")
#         .execute()
#     ).data

# # st.write("Summary Rows After Insert:", len(rock_summary))
# import pandas as pd
# # =====================================
# # POINT LOAD LOOKUP
# # =====================================

# pl_submissions = (
#     supabase
#     .table("point_load_submissions")
#     .select("id")
#     .eq("project_id", project_id)
#     .eq("review_status", "Approved")
#     .execute()
# ).data

# approved_pl_ids = {
#     row["id"]
#     for row in pl_submissions
# }

# pl_specimens = (
#     supabase
#     .table("point_load_specimens")
#     .select("*")
#     .execute()
# ).data

# point_load_lookup = {}

# for specimen in pl_specimens:

#     if specimen["submission_id"] in approved_pl_ids:

#         point_load_lookup[
#             specimen["rock_number"]
#         ] = specimen
# rdp_lookup = {}

# rdp_submissions = (
#     supabase
#     .table("rock_density_porosity_submissions")
#     .select("id")
#     .eq("project_id", project_id)
#     .eq("review_status", "Approved")
#     .execute()
# ).data

# approved_rdp = {
#     row["id"]
#     for row in rdp_submissions
# }

# rdp_specimens = (
#     supabase
#     .table("rock_density_porosity_observations")
#     .select("*")
#     .execute()
# ).data

# for specimen in rdp_specimens:

#     if specimen["submission_id"] in approved_rdp:

#         rdp_lookup[
#             specimen["rock_number"]
#         ] = specimen
# point_load_lookup = {}

# pl_submissions = (
#     supabase
#     .table("point_load_submissions")
#     .select("id")
#     .eq("project_id", project_id)
#     .eq("review_status", "Approved")
#     .execute()
# ).data

# approved_pl = {
#     row["id"]
#     for row in pl_submissions
# }

# pl_specimens = (
#     supabase
#     .table("point_load_specimens")
#     .select("*")
#     .execute()
# ).data

# for specimen in pl_specimens:

#     if specimen["submission_id"] in approved_pl:

#         point_load_lookup[
#             specimen["rock_number"]
#         ] = specimen
# ucs_lookup = {}

# ucs_submissions = (
#     supabase
#     .table("ucs_submissions")
#     .select("id")
#     .eq("project_id", project_id)
#     .eq("review_status", "Approved")
#     .execute()
# ).data

# approved_ucs = {
#     row["id"]
#     for row in ucs_submissions
# }

# ucs_specimens = (
#     supabase
#     .table("ucs_specimens")
#     .select("*")
#     .execute()
# ).data

# for specimen in ucs_specimens:

#     if specimen["submission_id"] in approved_ucs:

#         ucs_lookup[
#             specimen["rock_number"]
#         ] = specimen                
# summary_rows = []

# for row in rock_summary:

#     borehole = (
#         supabase
#         .table("boreholes")
#         .select("bh_no")
#         .eq("id", row["borehole_id"])
#         .execute()
#     ).data

#     bh_no = ""

#     if borehole:
#         bh_no = borehole[0]["bh_no"]
#     pl = point_load_lookup.get(
#         row["rock_number"],
#         {}
#     )
#     rdp = rdp_lookup.get(row["rock_number"], {})
#     pl = point_load_lookup.get(row["rock_number"], {})
#     ucs = ucs_lookup.get(row["rock_number"], {})
#     summary_rows.append({

#         "BH No": bh_no,

#         "Method of Drilling": row["method_of_drilling"],

#         "From": row["depth_from"],

#         "To": row["depth_to"],

#         "Rock No": row["rock_number"],

#         "Rock Sample Type": row["rock_sample_type"],

#         "Description": row["description"],

#         "CR %": row["cr_percent"],

#         "RQD %": row["rqd_percent"],

#         "Bulk Density": rdp.get("bulk_density"),
#         "Dry Density": rdp.get("dry_density"),
#         "Porosity": rdp.get("porosity"),

#         "Is(50)": pl.get("is50"),
#         "qc": pl.get("qc"),

#         "UCS": ucs.get("ucs"),

#     })

# summary_df = pd.DataFrame(summary_rows)
# edited_summary = st.data_editor(
#     summary_df,
#     use_container_width=True,
#     hide_index=True,
#     key="rock_summary_editor",
#     column_config={

#         "BH No": st.column_config.TextColumn(
#             "BH No",
#             disabled=True
#         ),

#         "Method of Drilling": st.column_config.TextColumn(
#             "Method of Drilling"
#         ),

#         "From": st.column_config.NumberColumn(
#             "From",
#             disabled=True,
#             format="%.2f"
#         ),

#         "To": st.column_config.NumberColumn(
#             "To",
#             disabled=True,
#             format="%.2f"
#         ),

#         "Rock No": st.column_config.TextColumn(
#             "Rock No",
#             disabled=True
#         ),

#         "Rock Sample Type": st.column_config.TextColumn(
#             "Rock Sample Type"
#         ),

#         "Description": st.column_config.TextColumn(
#             "Description"
#         ),

#         "CR %": st.column_config.NumberColumn(
#             "CR %",
#             format="%.2f"
#         ),

#         "RQD %": st.column_config.NumberColumn(
#             "RQD %",
#             format="%.2f"
#         ),

#         "Bulk Density": st.column_config.NumberColumn(
#             "Bulk Density",
#             disabled=True,
#             format="%.3f"
#         ),

#         "Dry Density": st.column_config.NumberColumn(
#             "Dry Density",
#             disabled=True,
#             format="%.3f"
#         ),

#         "Porosity": st.column_config.NumberColumn(
#             "Porosity",
#             disabled=True,
#             format="%.2f"
#         ),

#         "Is(50)": st.column_config.NumberColumn(
#             "Is(50)",
#             disabled=True,
#             format="%.2f"
#         ),

#         "qc": st.column_config.NumberColumn(
#             "qc",
#             disabled=True,
#             format="%.2f"
#         ),

#         "UCS": st.column_config.NumberColumn(
#             "UCS",
#             disabled=True,
#             format="%.2f"
#         ),

#     }
# )
# st.divider()

# if st.button(
#     "💾 Save Rock Summary",
#     use_container_width=True
# ):

#     for index, row in edited_summary.iterrows():

#         summary = rock_summary[index]

#         (
#             supabase
#             .table("rock_strength_summary")
#             .update({

#                 "method_of_drilling": row["Method of Drilling"],

#                 "rock_sample_type": row["Rock Sample Type"],

#                 "description": row["Description"],

#                 "cr_percent": row["CR %"],

#                 "rqd_percent": row["RQD %"]

#             })
#             .eq(
#                 "id",
#                 summary["id"]
#             )
#             .execute()
#         )

#     st.success("Rock Strength Summary Saved")

#     st.rerun()
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
# st.write("Borehole IDs:", borehole_ids)
# st.write("Samples:", samples)
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
# st.write("PL Submissions")
# st.write(pl_submissions)

# st.write("PL Lookup")
# st.write(pl_lookup) 
# # =====================================
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
    # pl = pl_lookup.get(
    #     (
    #         sample["borehole_id"],
    #         sample["sample_id"]
    #     )
    # )
    # # =========================
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
    # =====================================
    # ROCK STRENGTH SUMMARY
    # =====================================

st.divider()

st.header("Rock Strength Summary")
# =====================================
# LOAD ROCK SUMMARY
# =====================================

rock_summary = (
    supabase
    .table("rock_strength_summary")
    .select("*")
    .eq("project_id", project_id)
    .order("borehole_id")
    .order("depth_from")
    .execute()
).data

# st.write("Existing Summary Rows:", len(rock_summary))
# =====================================
# LOAD APPROVED ROCK DENSITY SUBMISSIONS
# =====================================

rdp_submissions = (
    supabase
    .table("rock_density_porosity_submissions")
    .select("*")
    .eq("project_id", project_id)
    .execute()
).data

# st.write(rdp_submissions)
# =====================================
# LOAD ROCK SPECIMENS
# =====================================

rdp_specimens = (
    supabase
    .table("rock_density_porosity_observations")
    .select("*")
    .execute()
).data
# =====================================
# LOAD APPROVED POINT LOAD
# =====================================

pl_submissions = (
    supabase
    .table("point_load_submissions")
    .select("*")
    .eq("project_id", project_id)
    .eq("review_status", "Approved")
    .execute()
).data

# st.write("Approved Point Load:", len(pl_submissions))
# =====================================
# LOAD POINT LOAD SPECIMENS
# =====================================

pl_specimens = (
    supabase
    .table("point_load_specimens")
    .select("*")
    .execute()
).data
approved_pl_ids = {
    row["id"]
    for row in pl_submissions
}

pl_specimens = [
    row
    for row in pl_specimens
    if row["submission_id"] in approved_pl_ids
]
pl_submission_lookup = {
    row["id"]: row
    for row in pl_submissions
}
# st.write("Approved Point Load Specimens:", len(pl_specimens))
# =====================================
# CREATE SUMMARY ROWS FROM POINT LOAD
# =====================================

for specimen in pl_specimens:
    submission = pl_submission_lookup[specimen["submission_id"]]
    existing = (
        supabase
        .table("rock_strength_summary")
        .select("id")
        .eq("project_id", project_id)
            .eq("borehole_id", submission["borehole_id"])
            .eq("rock_number", specimen["rock_number"])
            .execute()
        ).data

    if not existing:

            (
                supabase
                .table("rock_strength_summary")
                .insert({

                    "project_id": project_id,

                    "borehole_id": submission["borehole_id"],

                    "rock_number": specimen["rock_number"],

                    "method_of_drilling": None,

                    "depth_from": specimen["depth_from"],

                    "depth_to": specimen["depth_to"],

                    "rock_sample_type": None,

                    "description": None,

                    "cr_percent": None,

                    "rqd_percent": None

                })
                .execute()
            )
            rock_summary = (
        supabase
        .table("rock_strength_summary")
        .select("*")
        .eq("project_id", project_id)
        .order("depth_from")
        .execute()
    ).data

# st.write("Summary Rows After Insert:", len(rock_summary))
import pandas as pd
# =====================================
# POINT LOAD LOOKUP
# =====================================

pl_submissions = (
    supabase
    .table("point_load_submissions")
    .select("id")
    .eq("project_id", project_id)
    .eq("review_status", "Approved")
    .execute()
).data

approved_pl_ids = {
    row["id"]
    for row in pl_submissions
}

pl_specimens = (
    supabase
    .table("point_load_specimens")
    .select("*")
    .execute()
).data

point_load_lookup = {}

for specimen in pl_specimens:

    if specimen["submission_id"] in approved_pl_ids:

        point_load_lookup[
            specimen["rock_number"]
        ] = specimen
rdp_lookup = {}

rdp_submissions = (
    supabase
    .table("rock_density_porosity_submissions")
    .select("id")
    .eq("project_id", project_id)
    .eq("review_status", "Approved")
    .execute()
).data

approved_rdp = {
    row["id"]
    for row in rdp_submissions
}

rdp_specimens = (
    supabase
    .table("rock_density_porosity_observations")
    .select("*")
    .execute()
).data

for specimen in rdp_specimens:

    if specimen["submission_id"] in approved_rdp:

        rdp_lookup[
            specimen["rock_number"]
        ] = specimen
point_load_lookup = {}

pl_submissions = (
    supabase
    .table("point_load_submissions")
    .select("id")
    .eq("project_id", project_id)
    .eq("review_status", "Approved")
    .execute()
).data

approved_pl = {
    row["id"]
    for row in pl_submissions
}

pl_specimens = (
    supabase
    .table("point_load_specimens")
    .select("*")
    .execute()
).data

for specimen in pl_specimens:

    if specimen["submission_id"] in approved_pl:

        point_load_lookup[
            specimen["rock_number"]
        ] = specimen
ucs_lookup = {}

ucs_submissions = (
    supabase
    .table("ucs_submissions")
    .select("id,borehole_id")
    .eq("project_id", project_id)
    .eq("review_status", "Approved")
    .execute()
).data

ucs_submission_lookup = {
    row["id"]: row
    for row in ucs_submissions
}
st.write("UCS Lookup")
st.write(ucs_lookup)
ucs_specimens = (
    supabase
    .table("ucs_specimens")
    .select("*")
    .execute()
).data

for specimen in ucs_specimens:

    submission = ucs_submission_lookup.get(
        specimen["submission_id"]
    )

    if submission:

        ucs_lookup[
            (
                submission["borehole_id"],
                specimen["rock_number"]
            )
        ] = specimen
summary_rows = []
sg_lookup = {}

sg_submissions = (
    supabase
    .table("specific_gravity_submissions")
    .select("id,borehole_id")
    .eq("project_id", project_id)
    .eq("review_status", "Approved")
    .execute()
).data

sg_submission_lookup = {
    row["id"]: row
    for row in sg_submissions
}

sg_depths = (
    supabase
    .table("specific_gravity_depths")
    .select("*")
    .execute()
).data

for specimen in sg_depths:

    submission = sg_submission_lookup.get(
        specimen["submission_id"]
    )

    if submission and specimen.get("rock_number"):

        sg_lookup[
            (
                submission["borehole_id"],
                specimen["rock_number"]
            )
        ] = specimen

for row in rock_summary:

    borehole = (
        supabase
        .table("boreholes")
        .select("bh_no")
        .eq("id", row["borehole_id"])
        .execute()
    ).data

    bh_no = ""

    if borehole:
        bh_no = borehole[0]["bh_no"]
    pl = point_load_lookup.get(
        row["rock_number"],
        {}
    )
    rdp = rdp_lookup.get(row["rock_number"], {})
    pl = point_load_lookup.get(row["rock_number"], {})
    ucs = ucs_lookup.get(
    (
        row["borehole_id"],
        row["rock_number"]
    ),
    {}
)
    sg = sg_lookup.get(
    (
        row["borehole_id"],
        row["rock_number"]
    ),
    {}
)
    sample = (
        supabase
        .table("borehole_samples")
        .select("*")
        .eq("borehole_id", row["borehole_id"])
        .eq("depth", row["depth_from"])
        .limit(1)
        .execute()
    ).data
    st.write(
        "Looking for:",
        row["rock_number"]
    )

    st.write(
        "Found:",
        ucs_lookup.get(row["rock_number"])
    )

    sample = sample[0] if sample else {}
    summary_rows.append({

        "BH No": bh_no,

        "Method of Drilling": row["method_of_drilling"],

        "From": row["depth_from"],

        "To": row["depth_to"],

        "Rock No": row["rock_number"],

        "Rock Sample Type": sample.get("rock_sample_type"),

        "Description": row["description"],

        "CR %": sample.get("cr_percent"),

        "RQD %": sample.get("rqd_percent"),

        "Bulk Density": rdp.get("bulk_density"),
        "Dry Density": rdp.get("dry_density"),
        "Porosity": rdp.get("porosity"),
        "Specific Gravity": sg.get("specific_gravity"),

        "Is(50)": pl.get("is50"),
        "qc": pl.get("qc"),

        "UCS": ucs.get("ucs"),

    })

summary_df = pd.DataFrame(summary_rows)
edited_summary = st.data_editor(
    summary_df,
    use_container_width=True,
    hide_index=True,
    key="rock_summary_editor",
    column_config={

        "BH No": st.column_config.TextColumn(
            "BH No",
            disabled=True
        ),

        "Method of Drilling": st.column_config.TextColumn(
            "Method of Drilling"
        ),

        "From": st.column_config.NumberColumn(
            "From",
            disabled=True,
            format="%.2f"
        ),

        "To": st.column_config.NumberColumn(
            "To",
            disabled=True,
            format="%.2f"
        ),

        "Rock No": st.column_config.TextColumn(
            "Rock No",
            disabled=True
        ),

        "Rock Sample Type": st.column_config.TextColumn(
            "Rock Sample Type",
            disabled=True
        ),

        "Description": st.column_config.TextColumn(
            "Description"
        ),

        "CR %": st.column_config.NumberColumn(
            "CR %",
            format="%.2f",
            disabled=True
        ),

        "RQD %": st.column_config.NumberColumn(
            "RQD %",
            format="%.2f",
            disabled=True
        ),

        "Bulk Density": st.column_config.NumberColumn(
            "Bulk Density",
            disabled=True,
            format="%.3f"
        ),

        "Dry Density": st.column_config.NumberColumn(
            "Dry Density",
            disabled=True,
            format="%.3f"
        ),

        "Porosity": st.column_config.NumberColumn(
            "Porosity",
            disabled=True,
            format="%.2f"
        ),
        "Specific Gravity": st.column_config.NumberColumn(
            "Specific Gravity",
            disabled=True,
            format="%.3f"
        ),

        "Is(50)": st.column_config.NumberColumn(
            "Is(50)",
            disabled=True,
            format="%.2f"
        ),

        "qc": st.column_config.NumberColumn(
            "qc",
            disabled=True,
            format="%.2f"
        ),

        "UCS": st.column_config.NumberColumn(
            "UCS",
            disabled=True,
            format="%.2f"
        ),

    }
)
st.divider()

if st.button(
    "💾 Save Rock Summary",
    use_container_width=True
):

    for index, row in edited_summary.iterrows():

        summary = rock_summary[index]

        (
            supabase
            .table("rock_strength_summary")
            .update({

                "method_of_drilling": row["Method of Drilling"],

                "description": row["Description"]

            })
            .eq(
                "id",
                summary["id"]
            )
            .execute()
        )

    st.success("Rock Strength Summary Saved")

    st.rerun()