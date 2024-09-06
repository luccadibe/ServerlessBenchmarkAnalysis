import seaborn as sns
import matplotlib.pyplot as plt
from overview import *


def plot_cpu_test_data(df):
    # Filter data where status is 200 (successful requests)
    df_success = df[df["status"] == 200]

    # Filter data where status is 503 (unsuccessful requests)
    df_failure = df[df["status"] == 503]

    # Plotting fibDuration for successful requests across different providers and values of n
    plt.figure(figsize=(12, 6))
    sns.boxplot(x="n", y="fibDuration", hue="provider", data=df_success)
    plt.title("Fib Duration by Provider and n (Status == 200)")
    plt.show()

    # Plotting total_ms for both successful and unsuccessful requests across different providers and values of n
    plt.figure(figsize=(12, 6))
    sns.boxplot(x="n", y="total_ms", hue="provider", data=df)
    plt.title("Total Duration by Provider and n (Status 200 and 503)")
    plt.show()

    # Plotting ECDF for fibDuration for successful requests
    g = sns.FacetGrid(df_success, col="provider", hue="n", height=5, aspect=1.5)
    g.map(sns.ecdfplot, "fibDuration")
    g.add_legend()
    g.fig.suptitle("ECDF of fibDuration by Provider and n (Status == 200)", y=1.02)
    plt.show()

    # Plotting total_ms for successful requests across different providers and values of n
    plt.figure(figsize=(12, 6))
    sns.boxplot(x="n", y="total_ms", hue="provider", data=df_success)
    plt.title("Total Duration by Provider and n (Status == 200)")
    plt.show()


def plot_fibDurationVsWaitingTime(df):
    # Filter data where status is 200 (successful requests)
    df_success = df[df["status"] == 200]

    # Plotting waiting_ms against fibDuration for successful requests
    plt.figure(figsize=(12, 6))
    sns.scatterplot(
        x="waiting_ms", y="fibDuration", hue="provider", style="n", data=df_success
    )
    plt.title("Waiting Time vs Fib Duration by Provider (Status == 200)")
    plt.savefig("cputest_waiting_vs_fibduration.png")
    plt.show()


def plot_status(df, includeOutliers=True):
    if not includeOutliers:
        df = remove_outliers(df, "fibDuration", THRESHOLD)

    # Plotting the count of successful and unsuccessful requests
    # plt.figure(figsize=(12, 6))
    g = sns.FacetGrid(df, col="provider", row="n")
    g.map(sns.countplot, "status", hue="n", data=df, color=None)
    # plt.title("Count of Successful and Unsuccessful Requests", y=1.3, fontsize=16)
    plt.legend(title="n")
    plt.savefig(f"cputest_status_lattice_outliers{includeOutliers}.png")
    plt.show()


def plot_fibDuration(df, includeOutliers=True):
    if not includeOutliers:
        df = remove_outliers(df, "fibDuration", THRESHOLD)
    df_success = df[df["status"] == 200]
    # Plotting fibDuration for successful requests across different providers and values of n
    plt.figure(figsize=(12, 6))
    sns.boxplot(x="n", y="fibDuration", hue="provider", data=df_success)
    plt.title("Fib Duration by Provider and n (Status == 200)")
    plt.savefig(f"cputest_fibduration_outliers{includeOutliers}.png")
    plt.show()


df = get_data("CpuTest")
df = df[df["status"] != 500]
df = df[df["n"] != 38]
df = df[df["n"] != 15]
df = df[df["isCold"] == 0]
# plot_cpu_test_data(df)
#
# plot_fibDurationVsWaitingTime(df)
plot_status(df, includeOutliers=False)
plot_status(df, includeOutliers=True)

plot_fibDuration(df, includeOutliers=False)
plot_fibDuration(df, includeOutliers=True)
