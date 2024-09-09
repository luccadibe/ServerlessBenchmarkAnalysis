import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from overview import *


pd.set_option("display.max_colwidth", None)


#  identify the runtime based on the URL
def identify_runtime(row):
    if row["provider"] == "aws":
        if "osyk7zimdu4tctharhnu6j7xdy0jlkkw" in row["url"]:
            return "Node.js"
        else:
            return "Python"
    elif row["provider"] == "google":
        if "hellonode" in row["url"]:
            return "Node.js"
        elif "hellopython" in row["url"]:
            return "Python"
        else:
            return "Golang"
    elif row["provider"] == "flyio":
        if "hellogo" in row["url"]:
            return "Golang"
        else:
            return "Node.js"
    elif row["provider"] == "cloudflare":
        if "hellonode" in row["url"]:
            return "Node.js"
        else:
            return "Python"


# Load the data
data = get_data("ColdStart")

# Add the runtime column
data["runtime"] = data.apply(identify_runtime, axis=1)

# Filter data to only include cold starts (isCold == 1)
cold_data = data[data["isCold"] == 1]


def plot_boxplot(cold_data, includeOutliers=True):
    if not includeOutliers:
        cold_data = remove_outliers(cold_data, "waiting_ms", THRESHOLD)

    plt.figure(figsize=(12, 8))
    sns.violinplot(
        x="runtime",
        y="waiting_ms",
        hue="provider",
        data=cold_data,
        palette=PALETTE,
    )
    plt.title("Latency (waiting_ms) by Runtime and Provider")
    plt.xlabel("Runtime")
    plt.ylabel("Latency (ms)")
    # plt.yscale("log")
    plt.savefig(f"coldstarts-boxplot-outliers{includeOutliers}.png")
    plt.show()


def plot_boxplot_diff(cold_data):
    plt.figure(figsize=(12, 8))

    # Create a new column that combines runtime and provider for the x-axis labels
    cold_data["runtime_provider"] = cold_data["runtime"] + " - " + cold_data["provider"]

    # Update the palette to include all runtime-provider combinations
    palette = {
        "Node.js - aws": "#dbd642",
        "Python - aws": "#dbd642",
        "Node.js - google": "#374fd4",
        "Python - google": "#374fd4",
        "Golang - google": "#374fd4",
        "Node.js - flyio": "#6f32a8",
        "Golang - flyio": "#6f32a8",
        "Node.js - cloudflare": "orange",
        "Python - cloudflare": "orange",
    }

    sns.boxplot(x="runtime_provider", y="waiting_ms", data=cold_data, palette=palette)

    plt.title("Cold Start Latency  by Runtime and Provider")
    plt.xlabel("Runtime - Provider")
    plt.ylabel("Latency (ms)")
    # plt.yscale("log")
    plt.xticks(rotation=45, ha="right")  # Rotate x-axis labels for better readability
    # plt.savefig("coldstarts-boxplot.png")
    plt.show()


# Plotting CDF for the waiting_ms (latency)
def plot_cdf(cold_data):
    plt.figure(figsize=(10, 6))

    # Get unique runtimes and providers
    runtimes = cold_data["runtime"].unique()
    providers = cold_data["provider"].unique()

    for runtime in runtimes:
        plt.figure(figsize=(10, 6))
        plt.title(f"CDF of Cold Start Latency for {runtime}")

        for provider in providers:
            subset = cold_data[
                (cold_data["runtime"] == runtime) & (cold_data["provider"] == provider)
            ]

            if len(subset) > 0:
                sorted_latency = np.sort(subset["waiting_ms"])
                yvals = np.arange(1, len(sorted_latency) + 1) / float(
                    len(sorted_latency)
                )
                sns.ecdfplot(
                    subset["waiting_ms"], label=provider, color=PALETTE[provider]
                )
        plt.xscale("log")
        plt.xlabel("Latency (ms)")
        plt.ylabel("ECDF")
        plt.legend()
        plt.savefig(f"cdf_{runtime}.png")
        plt.show()


def plot_joy(data, includeOutliers):

    if not includeOutliers:
        data = remove_outliers(data, "waiting_ms", THRESHOLD)

    sns.set_theme(style="whitegrid")
    g = sns.FacetGrid(
        data,
        col="provider",
        hue="runtime",
        col_wrap=2,
        aspect=2,
        height=3,
        palette="tab10",
        margin_titles=False,
    )
    g.map(
        sns.kdeplot,
        "waiting_ms",
        fill=True,
        bw_adjust=0.2,
        common_norm=False,
        alpha=0.5,
    )
    g.set_axis_labels("Waiting Time (ms)", "")

    plt.xlim(0, 1500)
    # plt.savefig(f"coldstart-joyplot-outliers{includeOutliers}.png")
    plt.show()


plot_joy(cold_data, includeOutliers=False)
"""
plot_boxplot(cold_data, includeOutliers=False)
plot_boxplot(cold_data, includeOutliers=True)
plot_cdf(cold_data)
"""


# la de hellonode coldstart de aws es la q empieza con o
