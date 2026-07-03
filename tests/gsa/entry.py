import streamlit as st
import pandas as pd
from utils.database import supabase
import matplotlib.pyplot as plt
import numpy as np

from scipy.interpolate import PchipInterpolator
from tests.gsa.report import render_gsa_report
from tests.gsa.calculations import (
    calculate_gsa,
    calculate_summary,
    calculate_d_values,
    calculate_gradation_coefficients
)

DEFAULT_SIEVES = [

    "4.75",
    "2.00",
    "0.425", 
    "0.075",
    "Pan"

]


def render():
    

    sample = st.session_state.get(
        "selected_gsa_sample"
    )

    if not sample:

        st.error(
            "No Sample Selected"
        )

        return

    # =========================
    # BACK
    # =========================

    if st.button(
        "⬅ Back"
    ):

        st.session_state.pop(
            "selected_gsa_sample",
            None
        )

        st.session_state.pop(
            "selected_test_subpage",
            None
        )

        st.rerun()

    st.title(
        f"GSA - {sample['sample_id']}"
    )

    st.write(
        f"Depth : {sample['depth']} m"
    )

    st.write(
        f"Type : {sample['sample_type']}"
    )

    st.divider()

    # =========================
    # FIND / CREATE SUBMISSION
    # =========================
    st.write(sample)
    existing = (

            supabase
            .table(
                "gsa_submissions"
            )
            .select("*")
            .eq(
                "borehole_id",
                sample["borehole_id"]
            )
            .eq(
                "project_id",
                 st.session_state.get("selected_project")
            )
            .eq(
                "sample_id",
                sample["sample_id"]
            )
            .execute()

        ).data

    if existing:

        submission = existing[0]

    else:

        submission = (

            supabase
            .table(
                "gsa_submissions"
            )
            .insert({

                "project_id":
                st.session_state[
                    "selected_project"
                ],

                "borehole_id":
                st.session_state[
                    "selected_borehole"
                ],

                "sample_id":
                sample["sample_id"],

                "depth":
                sample["depth"]

            })
            .execute()

        ).data[0]
    # result = (
    #     supabase
    #     .table(
    #         "gsa_submissions"
    #     )
    #     .insert({
    #         ...
    #     })
    #     .execute()
    #     )

    # st.write(result)

    # submission = result.data[0]
    # =========================
# READ ONLY MODE
# =========================

    if submission.get(
        "status"
    ) == "Submitted":

        st.info(
            "Pending Review"
        )

        read_only = True

    else:

        read_only = False
    if submission.get("status") == "Draft":

        st.warning(
            "Draft Saved"
        )

    elif submission.get("status") == "Submitted":

        st.info(
            "Pending Review"
        )

        # =========================
    # LOAD SIEVES
    # =========================

    sieve_rows = (

        supabase
        .table(
            "gsa_sieves"
        )
        .select("*")
        .eq(
            "submission_id",
            submission["id"]
        )
        .execute()

    ).data

    existing_map = {

        r["sieve_size"]: r

        for r in sieve_rows

    }

    rows = []

    for sieve in DEFAULT_SIEVES:

        rows.append({

            "sieve_size":
            sieve,

            "retained_weight":

            float(

                existing_map
                .get(
                    sieve,
                    {}
                )
                .get(
                    "retained_weight",
                    0
                )

            )

        })

    # =========================
    # INPUT
    # =========================

    edited = []

    st.subheader(
        "Retained Weight"
    )
    
    for row in rows:

        wt = st.number_input(

            f"{row['sieve_size']} mm",

            min_value=0.0,

            value=float(
                row[
                    "retained_weight"
                ]
            ),
            disabled=read_only,
            
            key=row[
                "sieve_size"
            ]

        )

        edited.append({

            "sieve_size":
            row[
                "sieve_size"
            ],

            "retained_weight":
            wt

        })

    # =========================
    # CALCULATE
    # =========================

    calculated = calculate_gsa(
        edited
    )
    summary = calculate_summary(
    calculated
)
    st.subheader(
    "Calculated Results"
    )

    st.dataframe(
    pd.DataFrame(calculated),
    use_container_width=True,
    hide_index=True
    )

    render_gsa_report(
    calculated
    )
# =========================
# SAVE
# =========================

    if not read_only:

            c1, c2 = st.columns(2)

            with c1:

                if st.button(
                    "Save Draft",
                    use_container_width=True
                ):

                    (
                        supabase
                        .table(
                            "gsa_sieves"
                        )
                        .delete()
                        .eq(
                            "submission_id",
                            submission["id"]
                        )
                        .execute()
                    )

                    for row in calculated:

                        (
                            supabase
                            .table(
                                "gsa_sieves"
                            )
                            .insert({

                                "submission_id":
                                submission["id"],

                                "sieve_size":
                                row["sieve_size"],

                                "retained_weight":
                                row["retained_weight"],

                                "percent_retained":
                                row["percent_retained"],

                                "cumulative_retained":
                                row["cumulative_retained"],

                                "percent_passing":
                                row["percent_passing"]

                            })
                            .execute()
                        )

                    (
                        supabase
                        .table(
                            "gsa_submissions"
                        )
                        .update({

                            "gravel_percent":
                            summary["gravel"],

                            "sand_percent":
                            summary["sand"],

                            "silt_clay_percent":
                            summary["silt_clay"],

                            "status":
                            "Draft"

                        })
                        .eq(
                            "id",
                            submission["id"]
                        )
                        .execute()
                    )

                    st.success(
                        "Draft Saved"
                    )

                    st.rerun()

            with c2:

                if st.button(
                    "Final Submit",
                    type="primary",
                    use_container_width=True
                ):

                    # Save calculated values

                    (
                        supabase
                        .table(
                            "gsa_submissions"
                        )
                        .update({

                            "gravel_percent":
                            summary["gravel"],

                            "sand_percent":
                            summary["sand"],

                            "silt_clay_percent":
                            summary["silt_clay"],

                            "status":
                            "Submitted",

                            "review_status":
                            "Pending"

                        })
                        .eq(
                            "id",
                            submission["id"]
                        )
                        .execute()
                    )

                    # Create review queue item

                    existing_review = (

                        supabase
                        .table(
                            "reviews"
                        )
                        .select("*")
                        .eq(
                            "project_id",
                            st.session_state[
                                "selected_project"
                            ]
                        )
                        .eq(
                            "borehole_id",
                            st.session_state[
                                "selected_borehole"
                            ]
                        )
                        
                        .eq(
                            "test_name",
                            "Grain Size Analysis"
                        )
                        .execute()

                    ).data

                    if not existing_review:

                        (
                            supabase
                            .table(
                                "reviews"
                            )
                            .insert({

                                "project_id":
                                st.session_state[
                                    "selected_project"
                                ],

                                "borehole_id":
                                st.session_state[
                                    "selected_borehole"
                                ],

                                "test_name":
                                "Grain Size Analysis",

                                "status":
                                "Pending"

                            })
                            .execute()
                        )

                    st.success(
                        "Submitted For Review"
                    )

                    st.rerun()

                else:

                    st.info(
                        "Submission Locked - Awaiting Review"
                    )