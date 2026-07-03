import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd

from scipy.stats import linregress
from scipy.interpolate import make_interp_spline


def render_report(
    trials,
    show_spline=False,
    review_mode=False
):

    valid = [

        t

        for t in trials

        if (

            t["blows"] > 0

            and

            t["water_content"] is not None

        )

    ]

    if len(valid) < 2:

        st.info(
            "Minimum two valid trials required."
        )

        return

    blows = np.array(

        [

            t["blows"]

            for t in valid

        ],

        dtype=float

    )

    moisture = np.array(

        [

            t["water_content"]

            for t in valid

        ],

        dtype=float

    )

    log_blows = np.log10(
        blows
    )

    reg = linregress(
        log_blows,
        moisture
    )

    slope = reg.slope

    intercept = reg.intercept

    flow_index = abs(
        slope
    )

    r2 = reg.rvalue ** 2

    ll = (

        slope *

        np.log10(25)

        +

        intercept

    )

    x_fit = np.linspace(

        10,

        max(
            40,
            blows.max() + 5
        ),

        300

    )

    y_fit = (

        slope *

        np.log10(x_fit)

        +

        intercept

    )

    fig, ax = plt.subplots(

        figsize=(9,6)

    )

    # ---------------------------------
    # Observed Points
    # ---------------------------------

    ax.scatter(

        blows,

        moisture,

        s=80,

        color="royalblue",

        edgecolors="black",

        linewidths=0.8,

        zorder=10,

        label="Observed Points"

    )

    # ---------------------------------
    # Best Fit Line
    # ---------------------------------

    ax.plot(

        x_fit,

        y_fit,

        "--",

        color="navy",

        linewidth=1.5,

        alpha=0.8,

        label="Best Fit"

    )
# -------------------------------------
# Smooth Flow Curve (Semi-Log Spline)
# -------------------------------------

    order = np.argsort(blows)

    x_sorted = blows[order]
    y_sorted = moisture[order]

    log_x = np.log10(x_sorted)

    if len(x_sorted) >= 3:

        # Smooth interpolation in LOG space
        log_x_smooth = np.linspace(
            log_x.min(),
            log_x.max(),
            400
        )

        spline = make_interp_spline(
            log_x,
            y_sorted,
            k=min(2, len(x_sorted) - 1)
        )

        y_smooth = spline(log_x_smooth)

        # Convert back to actual blows
        x_smooth = 10 ** log_x_smooth

        if show_spline:

            ax.plot(
                x_smooth,
                y_smooth,
                color="royalblue",
        linewidth=2.5,
        zorder=3,
        label="Flow Curve"
        )

# When OFF, do nothing.
# The scatter points remain visible.
        # -------------------------------------
        # Regression Line (Used for LL)
        # -------------------------------------

            
        # if not show_spline:
        ax.plot(

            x_fit,

            y_fit,

            "--",

            color="navy",

            linewidth=1.2,

            alpha=0.7,

            label="Best Fit"

        )
            # ---------------------------------------
            # Liquid Limit Construction
            # ---------------------------------------

        ax.vlines(
            x=25,
            ymin=min(moisture),
            ymax=ll,
            colors="red",
            linestyles="--",
            linewidth=1.5
        )

        ax.hlines(
            y=ll,
            xmin=10,
            xmax=25,
            colors="red",
            linestyles="--",
            linewidth=1.5
        )

        ax.scatter(
            25,
            ll,
            color="red",
            s=80,
            zorder=10
        )
        ax.text(
        25.5,
        ll + 0.15,
        f"LL = {ll:.2f} %",
        color="red",
        fontsize=11,
        fontweight="bold"
    )
        ax.set_xscale("log")

        ax.set_xlim(
            10,
            max(
                40,
                blows.max() + 5
            )
        )

        ax.set_xticks([
            10,
            15,
            20,
            25,
            30,
            40,
            50
        ])

        ax.set_xticklabels([
            "10",
            "15",
            "20",
            "25",
            "30",
            "40",
            "50"
        ])

        ax.set_xlabel(
            "Blows (N)"
        )

        ax.set_ylabel(
            "Water Content (%)"
        )

        ax.set_title(
            "Flow Curve"
        )

        ax.grid(
            True,
            which="both",
            alpha=0.3
        )
        st.pyplot(
            fig
        )
        st.divider()

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "Liquid Limit",
            f"{ll:.2f} %"
        )

        c2.metric(
            "Flow Index",
            f"{flow_index:.2f}"
        )

        c3.metric(
            "R²",
            f"{r2:.3f}"
        )
        # import pandas as pd

        st.subheader("Trial Summary")
        if not review_mode:

            st.dataframe(

                pd.DataFrame({

            "Trial":[
                t["trial_no"]
                for t in valid
            ],

            "Blows":[
                t["blows"]
                for t in valid
            ],

            "Water Content (%)":[
                round(
                    t["water_content"],
                    2
                )
                for t in valid
            ]

        }),

        use_container_width=True,

        hide_index=True

    )