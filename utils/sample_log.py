from utils.database import supabase

def generate_sample_log(
    borehole_id,
    total_depth,
    first_sample_depth,
    first_sample_type
):

    current_depth = float(
        first_sample_depth
    )

    current_type = (
        first_sample_type
    )

    payload = []
    sample_no = 1

    while current_depth <= float(total_depth):

        payload.append({

            "borehole_id":
            borehole_id,
            "sample_id":
            f"SM-{sample_no:02d}",
            "depth":
            round(
                current_depth,
                2
            ),

            "sample_type":
            current_type

        })
        sample_no +=1

        current_depth += 1.5

        if current_type == "SPT":

            current_type = "UDS"

        else:

            current_type = "SPT"

    if payload:

        (
            supabase
            .table(
                "borehole_samples"
            )
            .insert(
                payload
            )
            .execute()
        )

        (
            supabase
            .table(
                "borehole_samples"
            )
            .insert({

                "borehole_id":
                borehole_id,
                "sample_id":
                f"SM-{sample_no:02d}",  
                "depth":
                round(
                    current_depth,
                    2
                ),

                "sample_type":
                current_type

            })
            .execute()
        )

        current_depth += 1.5

        if current_type == "SPT":

            current_type = "UDS"

        else:

            current_type = "SPT"


def get_sample_log(
borehole_id
):

    result = (
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
    )

    return result.data


def delete_sample_log(
    borehole_id
    ):


    (
        supabase
        .table(
            "borehole_samples"
        )
        .delete()
        .eq(
            "borehole_id",
            borehole_id
        )
        .execute()
    )


def save_sample_log(
borehole_id,
rows
):


    delete_sample_log(
        borehole_id
    )

    payload = []

    for row in rows:

        depth = row.get(
            "depth"
        )

        sample_type = row.get(
            "sample_type"
        )

        remarks = row.get(
            "remarks",
            ""
        )

        spt_n_value = row.get(
            "spt_n_value"
        )

        bulk_density = row.get(
            "bulk_density"
        )

        dry_unit_weight = row.get(
            "dry_unit_weight"
        )

        insitu_water_content = row.get(
            "insitu_water_content"
        )

        sample_id = row.get(
            "sample_id"
        )

        if (
            depth is None
            or sample_type is None
        ):
            continue

        payload.append({

            "borehole_id":
            borehole_id,

            "sample_id":
            sample_id,

            "depth":
            float(depth),

            "sample_type":
            str(sample_type),

            "remarks":
            str(remarks),

            "spt_n_value":
            spt_n_value,

            "bulk_density":
            bulk_density,

            "dry_unit_weight":
            dry_unit_weight,

            "insitu_water_content":
            insitu_water_content

        })

    if payload:

        (
            supabase
            .table(
                "borehole_samples"
            )
            .insert(
                payload
            )
            .execute()
        )