import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from overview import *

# Load the data from ColdStartSize table
data = get_data("ColdStartSize")

# Filter data to only include cold starts (isCold == 1)
cold_data = data[data["isCold"] == 1]


# Boxplot of Latency (waiting_ms) by Size
def plot_boxplot(cold_data):
    plt.figure(figsize=(12, 8))
    sns.boxplot(
        x="size",
        y="waiting_ms",
        data=cold_data,
        palette="viridis",
    )
    plt.title("Latency (waiting_ms) by Image Size")
    plt.xlabel("Image Size (Bytes)")
    plt.ylabel("Latency (ms)")
    plt.yscale("log")
    plt.xticks(rotation=45, ha="right")  # Rotate x-axis labels for better readability
    plt.savefig("coldstarts_size_boxplot.png")
    plt.show()


# Plotting CDF for the waiting_ms (latency)
def plot_cdf(cold_data):
    plt.figure(figsize=(10, 6))
    plt.title("CDF of Cold Start Latency")

    sorted_latency = np.sort(cold_data["waiting_ms"])
    yvals = np.arange(1, len(sorted_latency) + 1) / float(len(sorted_latency))

    sns.ecdfplot(cold_data["waiting_ms"], label="CDF", color="blue")

    plt.xscale("log")
    plt.xlabel("Latency (ms)")
    plt.ylabel("ECDF")
    plt.legend()
    plt.savefig("cdf_latency_size.png")
    plt.show()


plot_boxplot(cold_data)
plot_cdf(cold_data)
