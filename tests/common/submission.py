from utils.database import supabase

def get_or_create_submission(
    project_id,
    borehole_id,
    table_name
):

    submission = (
        supabase
        .table(table_name)
        .select("*")
        .eq("project_id", project_id)
        .eq("borehole_id", borehole_id)
        .execute()
    )

    if submission.data:

        return submission.data[0]

    response = (
        supabase
        .table(table_name)
        .insert({

            "project_id":
            project_id,

            "borehole_id":
            borehole_id,

            "status":
            "Draft",

            "is_locked":
            False

        })
        .execute()
    )

    return response.data[0] 