import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

from scipy.interpolate import PchipInterpolator

from tests.gsa.calculations import (
    calculate_gsa,
    calculate_summary,
    calculate_d_values,
    calculate_gradation_coefficients,
    classify_soil
)


def render_gsa_report(
    calculated
):

    summary = calculate_summary(
        calculated
    )

    d_values = calculate_d_values(
        calculated
    )

    coefficients = calculate_gradation_coefficients(
        d_values
    )

    soil = classify_soil(
        coefficients
    )

    graph_rows = []

    for row in calculated:

        if row["sieve_size"] != "Pan":

            graph_rows.append({

                "size": float(
                    row["sieve_size"]
                ),

                "passing":
                row["percent_passing"]

            })

    graph_rows.sort(
        key=lambda x: x["size"]
    )

    x = np.array(
        [r["size"] for r in graph_rows]
    )

    y = np.array(
        [r["passing"] for r in graph_rows]
    )

    curve = PchipInterpolator(
        x,
        y
    )

    xs = np.logspace(
        np.log10(x.min()),
        np.log10(x.max()),
        250
    )

    ys = curve(xs)

    fig, ax = plt.subplots(
        figsize=(8,6)
    )

    ax.plot(
        xs,
        ys,
        linewidth=2
    )

    ax.scatter(
        x,
        y,
        s=40,
        zorder=5
    )

    colors = {

        "D10":"red",

        "D30":"green",

        "D60":"purple"

    }

    levels = {

        "D10":10,

        "D30":30,

        "D60":60

    }

    for name in [

        "D10",

        "D30",

        "D60"

    ]:

        value = d_values[name]

        if value is None:
            continue

        level = levels[name]

        ax.scatter(

            value,

            level,

            color=colors[name],

            s=70,

            zorder=6

        )

        ax.vlines(

            value,

            0,

            level,

            colors=colors[name],

            linestyles="dashed"

        )

        ax.hlines(

            level,

            0.01,

            value,

            colors=colors[name],

            linestyles="dashed"

        )

        ax.text(

            value,

            level+2,

            name,

            color=colors[name],

            ha="center"

        )

    ax.set_xscale("log")

    ax.set_xlim(
        0.01,
        10
    )

    ax.set_ylim(
        0,
        100
    )

    ax.set_xticks([
        0.01,
        0.1,
        1,
        10
    ])

    ax.set_xticklabels([
        "0.01",
        "0.1",
        "1",
        "10"
    ])

    ax.set_xlabel(
        "Sieve Size (mm)"
    )

    ax.set_ylabel(
        "% Passing"
    )

    ax.grid(
        which="major"
    )

    ax.grid(
        which="minor",
        linestyle=":"
    )

    st.pyplot(fig)

    st.divider()

    st.subheader(
        "Characteristic Particle Sizes"
    )

    c1,c2,c3=st.columns(3)

    c1.metric(
        "D10",
        d_values["D10"]
    )

    c2.metric(
        "D30",
        d_values["D30"]
    )

    c3.metric(
        "D60",
        d_values["D60"]
    )

    st.subheader(
        "Summary"
    )

    c1,c2,c3=st.columns(3)

    c1.metric(
        "Gravel %",
        summary["gravel"]
    )

    c2.metric(
        "Sand %",
        summary["sand"]
    )

    c3.metric(
        "Silt + Clay %",
        summary["silt_clay"]
    )

    st.subheader(
        "Gradation Coefficients"
    )

    c1,c2=st.columns(2)

    c1.metric(
        "Cu",
        coefficients["Cu"]
    )

    c2.metric(
        "Cc",
        coefficients["Cc"]
    )

    if soil=="Well Graded Sand":

        st.success(
            soil
        )

    else:

        st.warning(
            soil
        )