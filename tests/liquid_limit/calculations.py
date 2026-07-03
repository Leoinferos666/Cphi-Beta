import numpy as np
import math
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

def calculate_liquid_limit(
    trials
):
    """
    trials =

    [

        {
            "blows":18,
            "water_content":42.3
        },

        ...
    ]
    """

    valid = []

    for t in trials:

        if (

            t["blows"] is not None

            and

            t["water_content"] is not None

        ):

            valid.append(t)

    if len(valid) < 2:

        return {

            "liquid_limit":None,

            "flow_index":None,

            "slope":None,

            "intercept":None

        }

    x = np.array(

        [

            math.log10(
                t["blows"]
            )

            for t in valid

        ]

    )

    y = np.array(

        [

            t["water_content"]

            for t in valid

        ]

    )

    slope, intercept = np.polyfit(
        x,
        y,
        1
    )

    ll = (

        slope *

        math.log10(25)

        +

        intercept

    )

    return {

        "liquid_limit":

        round(
            ll,
            2
        ),

        "flow_index":

        round(
            abs(slope),
            2
        ),

        "slope":slope,

        "intercept":intercept

    }