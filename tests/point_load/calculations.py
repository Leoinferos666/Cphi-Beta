import math

STANDARD_CORE_DIAMETER = 50.0


# ---------------------------------------
# Load (kN)
# ---------------------------------------

def calculate_load_kn(dial_gauge, dial_constant, entered_load):

    try:

        # Priority 1: Dial Gauge
        if dial_gauge not in [None, ""]:

            if dial_constant in [None, 0]:
                return None

            return dial_gauge * dial_constant

        # Priority 2: Manual Load
        if entered_load not in [None, ""]:

            return entered_load

        return None

    except:
        return None

# ---------------------------------------
# Failure Load (N)
# ---------------------------------------

def calculate_failure_load(load_kn):

    try:

        if load_kn is None:
            return None

        return load_kn * 1000.0

    except:
        return None


# ---------------------------------------
# D^(1.5) × (D*)^(0.5)
# ---------------------------------------

def calculate_d_factor(diameter, standard_diameter=STANDARD_CORE_DIAMETER):

    try:

        if diameter is None or diameter == 0:
            return None

        return (diameter ** 1.5) * math.sqrt(standard_diameter)

    except:
        return None


# ---------------------------------------
# Point Load Index Is(50)
# ---------------------------------------

def calculate_is50(failure_load, diameter):

    try:

        if failure_load is None:
            return None

        d_factor = calculate_d_factor(
            diameter,
            STANDARD_CORE_DIAMETER
        )

        if d_factor in [None, 0]:
            return None

        return failure_load / d_factor

    except:
        return None


# ---------------------------------------
# UCS Estimate qc
# ---------------------------------------

def calculate_qc(is50):

    try:

        if is50 is None:
            return None

        return 24 * is50

    except:
        return None