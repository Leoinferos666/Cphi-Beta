import math

STANDARD_CORE_DIAMETER = 50.0


def calculate_is50(
    failure_load,
    diameter
):
    """
    Temporary implementation.
    Replace with IS formula later.
    """

    try:

        if (
            failure_load is None
            or diameter is None
            or diameter == 0
        ):
            return None

        # Temporary formula
        return round(
            failure_load / (diameter ** 2),
            3
        )

    except:
        return None


def calculate_qc(is50):

    try:

        if is50 is None:
            return None

        return round(
            22 * is50,
            3
        )

    except:
        return None