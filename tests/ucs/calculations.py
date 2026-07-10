import math


def calculate_ld_ratio(length, diameter):

    try:
        if diameter in [0, None]:
            return None

        return length / diameter

    except:
        return None


def calculate_area(diameter):

    try:
        if diameter in [0, None]:
            return None

        return (3.14 * diameter * diameter) / 4

    except:
        return None


def calculate_volume(area, length):

    try:
        if area is None:
            return None

        return area * length

    except:
        return None


def calculate_bulk_density(weight, volume):

    try:
        if volume in [0, None]:
            return None

        return weight / volume

    except:
        return None


def calculate_ucs(failure_load, area):

    try:

        if failure_load is None or area in [0, None]:
            return None

        return (failure_load * 10) / area

    except:
        return None