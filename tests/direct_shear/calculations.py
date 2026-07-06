import math
import numpy as np


# ---------------------------------------------------
# Peak Shear Stress
# ---------------------------------------------------

def calculate_peak_shear_stress(peak_force, area):

    if area <= 0:
        return None

    return peak_force / area


# ---------------------------------------------------
# Direct Shear
# ---------------------------------------------------

def calculate_direct_shear(results):

    points = []

    for row in results:

        if (
            row["normal_stress"] > 0
            and row["peak_shear_stress"] is not None
        ):

            points.append(
                (
                    row["normal_stress"],
                    row["peak_shear_stress"]
                )
            )

    if len(points) < 2:

        return {
            "cohesion": None,
            "phi": None,
            "slope": None,
            "intercept": None
        }

    sigma = np.array([p[0] for p in points])
    tau = np.array([p[1] for p in points])

    slope, intercept = np.polyfit(
        sigma,
        tau,
        1
    )

    phi = math.degrees(
        math.atan(slope)
    )

    return {

        "cohesion": intercept,

        "phi": phi,

        "slope": slope,

        "intercept": intercept,

        "sigma": sigma,

        "tau": tau

    }