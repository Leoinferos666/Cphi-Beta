import streamlit as st

from utils.database import supabase


def render():

    borehole_id = st.session_state[
        "selected_borehole"
    ]

    samples = (

        supabase
        .table(
            "borehole_samples"
        )
        .select("*")
        .eq(
            "borehole_id",
            borehole_id
        )
        .order(
            "depth"
        )
        .execute()

    ).data

    st.title(
        "Plastic Limit"
    )

    for sample in samples:

        c1, c2 = st.columns(
            [4,1]
        )

        with c1:

            st.write(

                f"{sample['sample_id']}"

                f" | "

                f"{sample['depth']} m"

                f" | "

                f"{sample['sample_type']}"

            )

        with c2:

            if st.button(
                "Open",
                key=sample["id"]
            ):

                existing = (
                    supabase
                    .table("pl_submissions")
                    .select("*")
                    .eq(
                        "project_id",
                        st.session_state["selected_project"]
                    )
                    .eq(
                        "borehole_id",
                        borehole_id
                    )
                    .eq(
                        "sample_id",
                        sample["sample_id"]
                    )
                    .order("created_at", desc=True)
                    .limit(1)
                    .execute()
                ).data

                if existing:

                    submission = existing[0]

                else:

                    submission = (
                        supabase
                        .table("pl_submissions")
                        .insert({
                            "project_id": st.session_state["selected_project"],
                            "borehole_id": borehole_id,
                            "sample_id": sample["id"],
                            "status": "Draft",
                            "review_status": "Draft"
                        })
                        .execute()
                    ).data[0]
                
                    # st.stop()
                st.session_state["selected_pl_submission"] = submission["id"]
                st.session_state["selected_pl_sample"] = sample
                st.session_state["selected_test_subpage"] = "pl"

                st.rerun()