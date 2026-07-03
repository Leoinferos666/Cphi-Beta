def calculate_specific_gravity(
    m1,
    m2,
    m3,
    m4
):

    denominator = (
        (m4 - m1)
        -
        (m3 - m2)
    )

    if denominator <= 0:

        return None

    sg = (
        (m2 - m1)
        /
        denominator
    )

    return round(
        sg,
        3
    )