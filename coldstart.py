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
    # filter the data to only include cold starts
    cold_data = cold_data[cold_data["isCold"] == 1]
    # Get unique runtimes and providers
    runtimes = cold_data["runtime"].unique()
    providers = cold_data["provider"].unique()

    # Find global min and max for x-axis
    global_min = cold_data["waiting_ms"].min()
    global_max = cold_data["waiting_ms"].max()

    for runtime in runtimes:
        plt.figure(figsize=(10, 6))
        plt.title(f"Cold Start Latency for {runtime}")

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

        plt.xlim(global_min, global_max)
        plt.xscale("log")
        plt.title("")
        plt.xlabel("Latency (ms)")
        plt.ylabel("ECDF")
        plt.legend()
        plt.savefig(f"pdf/cold_start/coldstart_ecdf_{runtime}.pdf")
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
    plt.savefig(f"coldstart-joyplot-outliers{includeOutliers}.png")
    plt.show()


def plot_ecdf_flyio_golangvsnode(cold_data):
    plt.figure(figsize=(10, 6))
    plt.title("CDF of Cold Start Latency for Fly.io")
    cold_data = cold_data[cold_data["provider"] == "flyio"]

    sns.ecdfplot(
        cold_data[cold_data["runtime"] == "Golang"]["waiting_ms"],
        label="Golang",
        color="blue",
    )
    sns.ecdfplot(
        cold_data[cold_data["runtime"] == "Node.js"]["waiting_ms"],
        label="Node.js",
        color="yellow",
    )

    # checks : print the minimum and maximum values of the waiting_ms for each runtime
    print(
        "Golang min:",
        cold_data[cold_data["runtime"] == "Golang"]["waiting_ms"].min(),
    )
    print(
        "Golang max:",
        cold_data[cold_data["runtime"] == "Golang"]["waiting_ms"].max(),
    )
    print(
        "Node.js min:",
        cold_data[cold_data["runtime"] == "Node.js"]["waiting_ms"].min(),
    )
    print(
        "Node.js max:",
        cold_data[cold_data["runtime"] == "Node.js"]["waiting_ms"].max(),
    )

    # print tail latency (99th percentile)
    print(
        "Golang 99th percentile:",
        np.percentile(cold_data[cold_data["runtime"] == "Golang"]["waiting_ms"], 99),
    )
    print(
        "Node.js 99th percentile:",
        np.percentile(cold_data[cold_data["runtime"] == "Node.js"]["waiting_ms"], 99),
    )
    # print TMR (tail mean ratio)
    print(
        "Golang TMR:",
        np.percentile(cold_data[cold_data["runtime"] == "Golang"]["waiting_ms"], 99)
        / cold_data[cold_data["runtime"] == "Golang"]["waiting_ms"].mean(),
    )
    print(
        "Node.js TMR:",
        np.percentile(cold_data[cold_data["runtime"] == "Node.js"]["waiting_ms"], 99)
        / cold_data[cold_data["runtime"] == "Node.js"]["waiting_ms"].mean(),
    )

    plt.xscale("log")
    plt.xlabel("Latency (ms)")
    plt.ylabel("ECDF")
    # plt.xlim(0, 3500)
    plt.legend()
    plt.savefig(f"ecdf_flyio_nodevsgo.png")
    plt.show()


def get_coldstart_chance(data):
    # Per provider and runtime calculate the chance of a cold start
    coldstart_chance = data.groupby(["provider", "runtime"])["isCold"].mean()
    print(coldstart_chance)


# plot_cdf(cold_data)
# plot_joy(cold_data, includeOutliers=False)
"""
plot_boxplot(cold_data, includeOutliers=False)
plot_boxplot(cold_data, includeOutliers=True)

"""

# Load the data
data = get_data("ColdStart")

# Add the runtime column
data["runtime"] = data.apply(identify_runtime, axis=1)

# Filter data to only include cold starts (isCold == 1)
# cold_data = data[data["isCold"] == 1]
# plot_ecdf_flyio_golangvsnode(cold_data)
get_coldstart_chance(data)
# la de hellonode coldstart de aws es la q empieza con o


# inside the "body" column, there is a timestamp.
# it may be one of the 2 following formats:
# 1. "2024-09-10T13:15:05.90483441Z"
# 2. "1725974105119"
# we need to convert the second format to the first one
# then study the difference between body and start timestamp

from datetime import datetime


# Function to convert timestamp in body column to a uniform format (ISO 8601)
def convert_body_timestamp(body):
    try:
        # If it's in ISO 8601 format (Z indicates UTC), parse as a timezone-aware datetime
        return pd.to_datetime(body, utc=True)
    except ValueError:
        # If it's in Unix epoch format (milliseconds), convert to UTC datetime
        try:
            timestamp_ms = int(body)
            return pd.to_datetime(timestamp_ms, unit="ms", utc=True)
        except ValueError:
            return np.nan  # Handle any non-parsable values


pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)


# Function to calculate latency and generate summary table
def network_latency_summary(df):
    # Convert body timestamps to datetime
    df["body_timestamp"] = df["body"].apply(convert_body_timestamp)
    df["start_timestamp"] = pd.to_datetime(df["start"])

    # Calculate network latency (in milliseconds)
    df["latency_ms"] = (
        df["body_timestamp"] - df["start_timestamp"]
    ).dt.total_seconds() * 1000

    # Group by provider and runtime to calculate statistics
    summary = (
        df.groupby(["provider", "runtime"])["latency_ms"]
        .agg(
            min_latency="min",
            mean_latency="mean",
            median_latency="median",
            p99_latency=lambda x: np.percentile(x, 99),
            max_latency="max",
        )
        .reset_index()
    )
    summary.to_excel("network_latency_summary.xlsx", index=False)
    return summary


plot_cdf(data)
# print(network_latency_summary(data))
