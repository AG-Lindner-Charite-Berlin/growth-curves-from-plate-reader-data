import numpy as np
import pandas as pd
from typing import Literal
import matplotlib.pyplot as plt
from utils import get_valid_filename
from models import GrowthCurveConfig, Experiment, PlotConfig


def run_plotting_pipeline(
    plot_title,
    path_to_raw_data: str,
    path_to_plate_layout: str,
    conditions: list[str],
    strains: list[str],
    media: list[str],
    groupby: Literal["strain", "condition", "medium"],
):
    import json
    from matplotlib import pyplot as plt
    from models import GrowthCurveConfig, PlotConfig, Experiment
    from plotting import plot_no_numbers

    # load plate layout
    with open(path_to_plate_layout, "r") as f:
        plate_layout = json.load(f)

    # filter plate layout by conditions
    wells = plate_layout
    if not conditions[0] == "all":
        wells = list(filter(lambda well: well["condition"] in conditions, plate_layout))
    # filter plate layout by strains
    if not strains[0] == "all":
        wells = list(filter(lambda well: well["strain"] in strains, wells))
    # filter plate layout by strains
    if not media[0] == "all":
        wells = list(filter(lambda well: well["medium"] in media, wells))

    growth_curves = []

    # zip replicate pairs
    r1 = filter(lambda well: well["replicate"] == "1", wells)
    r2 = filter(lambda well: well["replicate"] == "2", wells)

    def label_condition(well):
        if groupby == "strain":
            return f"{well['strain']} {well['medium']}"
        elif groupby == "condition":
            return well["condition"]
        elif groupby == "medium":
            return well["medium"]

    # iterate over replicate pairs
    for wells in zip(r1, r2):
        growth_curves.append(
            GrowthCurveConfig(
                measurement_series=[
                    wells[0]["well"],
                    wells[1]["well"],
                ],
                aggregation_func="mean",
                condition=label_condition(wells[0]),
                line_style="solid" if wells[0]["medium"] == "MX" else "dotted",
            )
        )

    experiment = Experiment(
        title=plot_title,
        path_to_raw_data=path_to_raw_data,
        sheet_name="Sheet1",
        growth_curve_configs=growth_curves,
        measurement_period=10,
        OD_growth_threshold=0.05,
    )

    plot_config = PlotConfig(
        y_scale="linear", x_max=None, y_max=None, save_plot_as="png", is_mean_plot=True
    )

    plt.close("all")  # close all graph windows

    plt.subplots_adjust(right=0.65, top=1.1)

    # plot the growth curves
    plot_no_numbers(
        experiment=experiment,
        plot_config=plot_config,
    )


def plot(
    data, MATS, WIN, TH, Figure_Type, Yscale, Xmax, Ymax, cmap, linestyles, savefig="no"
):
    from scipy.stats import linregress

    for mat in MATS.loc[2]:
        slope = np.array([])
        timePoint = np.array([])
        biomassYield = np.array([])
        for id in mat:
            v = data[id]
            if np.amax(v) < TH:
                # 0.001 is just a number small enough
                slope = np.append(slope, 0.00001)
                timePoint = np.append(timePoint, np.inf)
                biomassYield = np.append(biomassYield, np.amax(v))
                continue
            else:
                rate_tmp = np.array([])
                for tp in v.index:
                    P = linregress(
                        v.loc[tp : tp + WIN].index.values, np.log(v.loc[tp : tp + WIN])
                    )
                    # more: intercept, rvalue, pvalue, stderr
                    rate_tmp = np.append(rate_tmp, P.slope)
                slope = np.append(slope, np.nanmax(rate_tmp))
                timePoint = np.append(timePoint, v.index.values[np.nanargmax(rate_tmp)])
                biomassYield = np.append(biomassYield, np.amax(v))

        doubling_time = np.around(np.log(2) / slope, 1)
        doubling_time_mean = np.around(np.nanmean(doubling_time), 1)
        doubling_time_sd = np.around(np.nanstd(doubling_time), 1)
        # doubling_time_sem = np.around(sem(doubling_time), 1)
        time_start_mean = np.around(np.nanmean(timePoint), 1)
        time_start_sd = np.around(np.nanstd(timePoint), 1)
        # time_start_sem = np.around(sem(timePoint), 1)
        biomassYield_mean = np.around(np.nanmean(biomassYield), 2)
        biomassYield_sd = np.around(np.nanstd(biomassYield), 1)
        # biomassYield_sem = np.around(sem(biomassYield), 1)

        if doubling_time_mean < 150:
            MATS.loc[3][MATS.loc[2].index(mat)] = (
                MATS.loc[3][MATS.loc[2].index(mat)]
                + ": "
                + str(doubling_time_mean)
                + "("
                + str(doubling_time_sd)
                + ")"
                ", " + str(time_start_mean) + "(" + str(time_start_sd) + ")"
            )  # ', ' \
            # + str(biomassYield_mean) + '(' \
            # + str(biomassYield_sd) + ')'
        else:
            MATS.loc[3][MATS.loc[2].index(mat)] = (
                MATS.loc[3][MATS.loc[2].index(mat)] + ": NG"
            )

    # ploting all/mean
    fig, ax = plt.subplots(figsize=(20, 10))
    lines = []
    line_num = []

    for mat in MATS.loc[2]:
        i = MATS.loc[2].index(mat)
        if Figure_Type == "mean":
            line_num.append(len(lines))
            lines += ax.plot(
                data.index,
                data[mat].mean(axis=1),
                linestyle=linestyles[i],
                color=cmap[i],
                linewidth=3,
            )  # label=MATS[3][i]
        elif Figure_Type == "all":
            line_num.append(len(lines))
            lines += ax.plot(
                data.index,
                data[mat],
                label=MATS[3][i],
                linestyle=linestyles[i],
                color=cmap[i],
                linewidth=3,
            )

    ax.grid(which="major", axis="x", linewidth=1, linestyle="-", color="0.75")
    ax.grid(which="major", axis="y", linewidth=1, linestyle="--", color="0.75")
    ax.tick_params(
        which="both",
        direction="in",
        bottom=True,
        right=False,
        top=False,
        left=True,
        labelsize=18,
        width=2,
        length=4,
    )
    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)
    ax.set_yscale(Yscale)

    if Yscale == "log":
        ax.set_ylim(top=Ymax)
    elif Yscale == "linear":
        ax.set_ylim(bottom=0, top=Ymax)

    ax.set_title(MATS[1], fontsize=24)
    ax.set_ylabel("OD600", fontsize=20)
    ax.set_xlabel("Time (h)", fontsize=20)
    ax.set_xlim(left=0, right=Xmax)
    ax.legend(
        [lines[i] for i in line_num],
        MATS[3][:],
        fontsize=16,
        loc="center left",
        bbox_to_anchor=(1, 0.6),
        fancybox=True,
        shadow=True,
        ncol=1,
    )
    plt.subplots_adjust(right=0.65)

    if savefig != "no":
        title = get_valid_filename(MATS[1])
        fig.savefig("{}_{}.{}".format(Figure_Type, title, savefig), dpi=300)


def plot_plate(data, well_count=96):
    """
    Plot all wells in a plate
    """
    if well_count not in [96, 48]:
        raise ValueError("only 96 and 48 wells are supported")

    nrows = 8 if well_count == 96 else 6
    ncols = 12 if well_count == 96 else 8

    row = ["A", "B", "C", "D", "E", "F", "G", "H"]
    col = list(range(1, 13))

    fig, axes = plt.subplots(nrows=nrows, ncols=ncols, sharex=True, sharey=True)
    fig.set_size_inches(15, 10)

    for i in range(nrows):
        for j in range(ncols):
            well = row[i] + str(col[j])
            if well in data.columns.values.tolist():
                axes[i, j].plot(data.index, data.loc[:, well], linewidth=3)

    plt.show()


def plot_wells(wells, data):
    """Please enter wells in list, e.g. ['A1','A2',]"""
    ID = data.columns.values.tolist()
    plt.figure(figsize=(12, 10))
    if np.all(np.isin(wells, ID)):
        plt.plot(data.index, data.loc[:, wells], linewidth=3)
        plt.legend(wells)
        plt.show()
    else:
        print("Please enter valid wells, e.g. ['A1','A2','A3']")


def plot_no_numbers(experiment: Experiment, plot_config: PlotConfig) -> None:
    """Plot growth curves without numbers on the plot.

    Args:
        data (pd.DataFrame): data to plot
        title (str): title of the plot
        growth_curve_configs (list[GrowthCurveConfig]): list of GrowthCurveConfig
        is_mean_plot (bool): whether to plot mean or all growth curves
        y_scale (Literal["linear", "log", "symlog", "logit"]): y-axis scale
        x_max (float | None): maximum value of x-axis
        y_max (float | None): maximum value of y-axis
        save_plot_as (str, optional): file format to save the plot. Defaults to "no".
    """

    # ploting all/mean
    fig, ax = plt.subplots(figsize=(20, 10))
    lines = []
    line_num = []

    curr_color_idx = 0

    # plot all growth curves
    for idx, growth_curve in enumerate(experiment.growth_curve_configs):
        line_num.append(len(lines))

        growth_curve_data = (
            experiment.adjusted_growth_data[growth_curve.measurement_series].mean(
                axis=1
            )
            if plot_config.is_mean_plot
            else experiment.adjusted_growth_data[growth_curve.measurement_series]
        )

        lines += ax.plot(
            experiment.adjusted_growth_data.index,
            growth_curve_data,
            label=growth_curve.condition,
            linestyle=plot_config.default_line_style
            if not growth_curve.line_style
            else growth_curve.line_style,
            color=plot_config.default_color_palette[
                idx % len(plot_config.default_color_palette)
            ]
            if not growth_curve.line_color
            else growth_curve.line_color,
            linewidth=5,
        )

    ax.grid(which="major", axis="x", linewidth=2, linestyle="-", color="0.75")
    ax.grid(which="major", axis="y", linewidth=2, linestyle="--", color="0.75")
    ax.grid(which="minor", axis="y", linewidth=0.5, linestyle="--", color="0.75")
    ax.tick_params(
        which="both",
        direction="in",
        bottom=True,
        right=False,
        top=False,
        left=True,
        labelsize=18,
        width=2,
        length=4,
    )
    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)
    ax.set_yscale(plot_config.y_scale)

    ax.set_ylim(bottom=0, top=plot_config.y_max)

    ax.set_title(experiment.title, fontsize=24)
    ax.set_ylabel("cuvette $OD_{600}$", fontsize=20)
    ax.set_xlabel("time (h)", fontsize=20)
    ax.set_xlim(left=0, right=plot_config.x_max)
    ax.legend(
        [lines[i] for i in line_num],
        [config.condition for config in experiment.growth_curve_configs],
        fontsize=20,
        loc="center left",
        bbox_to_anchor=(1, 0.6),
        fancybox=True,
        shadow=True,
        ncol=1,
    )
    plt.subplots_adjust(right=0.65)

    # save figure if file format is specified
    if plot_config.save_plot_as != "no":
        fig.savefig(
            f"{'mean' if plot_config.is_mean_plot else 'all'}_{get_valid_filename(experiment.title)}.{plot_config.save_plot_as}",
            dpi=300,
        )
