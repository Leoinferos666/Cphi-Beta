# import numpy as np
# import math
def calculate_water_content(
    container_weight,
    wet_soil_container,
    dry_soil_container
):

    try:

        water_weight = (
            wet_soil_container -
            dry_soil_container
        )

        dry_soil_weight = (
            dry_soil_container -
            container_weight
        )

        if dry_soil_weight <= 0:

            return None

        moisture = (

            water_weight /

            dry_soil_weight

        ) * 100

        return {

            "water_content": round(
                moisture,
                2
            ),

            "water_weight": round(
                water_weight,
                2
            ),

            "dry_soil_weight": round(
                dry_soil_weight,
                2
            )

        }

    except:

        return None

def calculate_plastic_limit(trials):
    """
    trials = [
        {
            "water_content": 24.5
        },
        ...
    ]
    """

    valid = [
        t["water_content"]
        for t in trials
        if t["water_content"] is not None
    ]

    if len(valid) == 0:
        return {
            "plastic_limit": None
        }

    plastic_limit = sum(valid) / len(valid)

    return {
        "plastic_limit": round(plastic_limit, 2)
    }