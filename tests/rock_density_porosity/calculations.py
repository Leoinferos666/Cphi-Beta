def calculate_density(m1, m2, m3, m4, m5):
    """
    Density = (M5 - M1) / ((M4 - M1) - (M3 - M2))
    """

    try:
        denominator = (m4 - m1) - (m3 - m2)

        if denominator == 0:
            return 0.0

        return round((m5 - m1) / denominator, 3)

    except Exception:
        return 0.0


def calculate_porosity(m1, m2, m3, m4, m5):
    """
    Porosity (%) =
    ((M4 - M1) - (M5 - M1))
    /
    ((M4 - M1) - (M3 - M2))
    × 100
    """

    try:
        denominator = (m4 - m1) - (m3 - m2)

        if denominator == 0:
            return 0.0

        numerator = (m4 - m1) - (m5 - m1)

        return round((numerator / denominator) * 100, 2)

    except Exception:
        return 0.0
    
        