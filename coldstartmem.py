import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from overview import *

# Load the data from ColdStartMem table
data = get_data("ColdStartMem")

# Filter data to only include cold starts (isCold == 1)
cold_data = data[data["isCold"] == 1]

# Get the data for flyio with memory = 256MB (its in ColdStart table)
fly = get_data("ColdStart")
flyio_256 = fly[(fly["provider"] == "flyio")]

# Add the memory column

flyio_256["memory"] = 256

# Merge the data

cold_data = pd.concat([cold_data, flyio_256])

# take out rows cause by bugs for flyio with memory = 1024
cold_data = cold_data[
    ~(
        (cold_data["provider"] == "flyio")
        & (cold_data["memory"] == 1024)
        & (cold_data["waiting_ms"] < 200)
    )
]


# Boxplot of Latency (waiting_ms) by Memory Allocation
def plot_boxplot(cold_data):
    plt.figure(figsize=(12, 8))
    sns.boxplot(
        x="memory",
        y="waiting_ms",
        data=cold_data,
        palette=PALETTE,
    )
    plt.title("Latency (waiting_ms) by Memory Allocation")
    plt.xlabel("Memory Allocation (MB)")
    plt.ylabel("Latency (ms)")
    plt.yscale("log")
    plt.xticks(rotation=45, ha="right")  # Rotate x-axis labels for better readability
    plt.savefig("coldstarts_memory_boxplot.png")
    plt.show()


def plot_boxplot_grid(cold_data, includeOutliers=True):
    if not includeOutliers:
        cold_data = remove_outliers(cold_data, "waiting_ms", THRESHOLD)

    # control: print max , min and median of waiting_ms for each memory config and provider
    print(
        cold_data.groupby(["memory", "provider"])["waiting_ms"].agg(
            ["max", "min", "median"]
        )
    )

    g = sns.FacetGrid(cold_data, col="provider", hue="provider", palette=PALETTE)
    g.map(sns.violinplot, "memory", "waiting_ms")
    g.set_titles("{col_name}")
    g.set_xlabels("Memory Allocation (MB)")
    g.set_ylabels("Latency (ms)")
    plt.savefig(f"coldstarts_memory_boxplot_grid_outliers{includeOutliers}.png")
    plt.show()


# Plotting ECDF for the waiting_ms (latency)
def plot_cdf(cold_data, includeOutliers=True):
    if not includeOutliers:
        cold_data = remove_outliers(cold_data, "waiting_ms", THRESHOLD)
    g = sns.FacetGrid(cold_data, col="provider", hue="provider", palette=PALETTE)
    g.map(sns.ecdfplot, "waiting_ms")
    g.add_legend()
    plt.xscale("log")
    plt.xlabel("Latency (ms)")
    plt.ylabel("ECDF")
    plt.savefig("cdf_latency_memory.png")
    plt.show()


def plot_distribution(cold_data, provider, memory, includeOutliers=True):
    if not includeOutliers:
        cold_data = remove_outliers(cold_data, "waiting_ms", THRESHOLD)
    cold_data = cold_data[
        (cold_data["provider"] == provider) & (cold_data["memory"] == memory)
    ]
    sns.histplot(cold_data["waiting_ms"], kde=True)
    plt.title(f"Latency Distribution for {provider} with {memory}MB memory")
    plt.xlabel("Latency (ms)")
    plt.ylabel("Frequency")
    plt.savefig(f"latency_distribution_{provider}_{memory}.png")
    plt.show()


# plot_boxplot(cold_data)
# plot_cdf(cold_data, includeOutliers=False)
plot_boxplot_grid(cold_data, includeOutliers=False)

plot_distribution(cold_data, "flyio", 1024, includeOutliers=True)
