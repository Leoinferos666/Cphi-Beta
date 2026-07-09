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

        return math.pi * diameter * diameter / 4

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
        if area in [0, None]:
            return None

        # kN → N
        load = failure_load * 1000

        # cm² → mm²
        area_mm2 = area * 100

        return load / area_mm2

    except:
        return None