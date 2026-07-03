import numpy as np
from scipy.interpolate import PchipInterpolator
def calculate_gsa(rows):

    total = sum(
        r["retained_weight"]
        for r in rows
    )

    if total == 0:

        for row in rows:

            row["percent_retained"] = 0

            row["cumulative_retained"] = 0

            row["percent_passing"] = 0

        return rows
    cumulative = 0

    for row in rows:

        percent_retained = (
            row["retained_weight"]
            / total
        ) * 100

        cumulative += percent_retained

        row["percent_retained"] = round(
            percent_retained,
            2
        )

        row["cumulative_retained"] = round(
            cumulative,
            2
        )

        row["percent_passing"] = round(
            100 - cumulative,
            2
        )

    return rows


def calculate_summary(rows):

    gravel = 0

    passing_475 = 0

    passing_0075 = 0

    for row in rows:

        sieve = str(
            row["sieve_size"]
        )

        if sieve == "4.75":

            gravel = round(
                row[
                    "cumulative_retained"
                ],
                2
            )

            passing_475 = row[
                "percent_passing"
            ]

        elif sieve == "0.075":

            passing_0075 = row[
                "percent_passing"
            ]

    sand = round(
        passing_475
        -
        passing_0075,
        2
    )

    silt_clay = round(
        passing_0075,
        2
    )

    return {

        "gravel":
        gravel,

        "sand":
        sand,

        "silt_clay":
        silt_clay

    }
def calculate_d_values(rows):
   

    graph_rows = []

    for row in rows:

        sieve = str(
            row["sieve_size"]
        )

        if sieve.lower() != "pan":

            graph_rows.append({

                "size":
                float(sieve),

                "passing":
                row["percent_passing"]

            })

    if len(graph_rows) < 2:

        return {

            "D10": None,

            "D30": None,

            "D60": None

        }

    graph_rows.sort(
        key=lambda x: x["size"]
    )

    x = np.array(

        [

            r["size"]

            for r in graph_rows

        ]

    )

    y = np.array(

        [

            r["passing"]

            for r in graph_rows

        ]

    )

    try:

        interp = PchipInterpolator(
            x,
            y
        )

        xs = np.logspace(

            np.log10(x.min()),

            np.log10(x.max()),

            5000

        )

        ys = interp(xs)

        def get_d(target):

            idx = np.argmin(

                np.abs(

                    ys - target

                )

            )

            return round(

                float(xs[idx]),

                4

            )

        return {

            "D10":
            get_d(10),

            "D30":
            get_d(30),

            "D60":
            get_d(60),
            
            "curve": interp

        }

    except:

        return {

            "D10": None,

            "D30": None,

            "D60": None

        }
def calculate_gradation_coefficients(
    d_values
):

    d10 = d_values["D10"]
    d30 = d_values["D30"]
    d60 = d_values["D60"]

    if None in (
        d10,
        d30,
        d60
    ):

        return {

            "Cu": None,

            "Cc": None

        }

    cu = round(

        d60 / d10,

        2

    )

    cc = round(

        (d30 ** 2) /

        (d10 * d60),

        2

    )

    return {

        "Cu": cu,

        "Cc": cc

    }
def classify_soil(coefficients):

    cu = coefficients["Cu"]
    cc = coefficients["Cc"]

    if cu is None or cc is None:
        return "Unknown"

    if cu >= 6 and 1 <= cc <= 3:
        return "Well Graded Sand"

    return "Poorly Graded Sand"