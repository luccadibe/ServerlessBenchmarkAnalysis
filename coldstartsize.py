from overview import *

# Load the data from ColdStartSize table
data = get_data("ColdStartSize")

# Filter data to only include cold starts (isCold == 1)
cold_data = data[data["isCold"] == 1]


# Boxplot of Latency (waiting_ms) by Size
def plot_boxplot(cold_data):
    # plt.figure(figsize=(12, 8))
    sns.boxplot(
        x="size",
        y="waiting_ms",
        data=cold_data,
        hue="provider",
        palette=PALETTE,
    )
    plt.title("Latency (waiting_ms) by Image Size")
    plt.xlabel("Image Size (Bytes)")
    plt.ylabel("Latency (ms)")
    # plt.yscale("log")
    # plt.xticks(rotation=45, ha="right")  # Rotate x-axis labels for better readability
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


def plot_scatter(cold_data):
    plt.figure(figsize=(10, 6))
    plt.title("Scatter Plot of Cold Start Latency by Image Size")
    sns.scatterplot(
        x="size",
        y="waiting_ms",
        data=cold_data,
        hue="provider",
        palette=PALETTE,
    )
    plt.xlabel("Image Size (Bytes)")
    plt.ylabel("Latency (ms)")
    plt.ylim(0, 250)
    plt.legend(title="Provider")
    plt.savefig("scatter_latency_size.png")
    plt.show()


# between index 5 and 10 is the month - day

print(cold_data[cold_data["id"] == 1].iloc[0]["start"][5:10])


def plot_day(cold_data, includeOutliers=True):
    if not includeOutliers:
        cold_data = remove_outliers(cold_data, "waiting_ms", THRESHOLD)

    # Convert the 'start' column to datetime format
    cold_data["start"] = pd.to_datetime(cold_data["start"])
    # take out size=100 because n=1 for size=100
    cold_data = cold_data[cold_data["size"] != 100]
    # Extract the hour from the 'start' timestamp to analyze the time of day
    cold_data["hour"] = cold_data["start"].dt.hour

    # check n by hour
    a = {}
    print(cold_data["hour"].unique())
    for h in cold_data["hour"]:
        if a.get(h) is None:
            a[h] = 1
        else:
            a[h] += 1
    print(a)

    # Print the different sizes and their counts
    sizes = cold_data["size"].unique()
    print(f"Number of different sizes: {len(sizes)}")
    print(f"Sizes: {sizes}")

    # Print statistics for each size
    print("\nStatistics per size:")
    for size in sizes:
        size_data = cold_data[cold_data["size"] == size]["waiting_ms"]

        n = len(size_data)
        std_dev = size_data.std()
        five_num_summary = size_data.describe(percentiles=[0.25, 0.5, 0.75])

        print(f"\nSize: {size}")
        print(f"Count (n): {n}")
        print(f"Standard Deviation: {std_dev:.2f}")
        print(f"5-Number Summary:")
        print(f"Min: {five_num_summary['min']}")
        print(f"25th Percentile (Q1): {five_num_summary['25%']}")
        print(f"Median (Q2): {five_num_summary['50%']}")
        print(f"75th Percentile (Q3): {five_num_summary['75%']}")
        print(f"Max: {five_num_summary['max']}")

    # Create a plot with seaborn
    # plt.figure(figsize=(12, 6))
    sns.lineplot(
        data=cold_data,
        x="hour",
        y="waiting_ms",
        hue="size",
        marker="o",
        estimator=np.median,
        errorbar=None,
        legend="full",
    )

    # Customize the plot
    plt.title("Cold Start Latency by Hour and Size")
    plt.xlabel("Hour of the Day")
    plt.ylabel("Latency (ms)")

    # Adjust the legend to be outside the plot
    # plt.legend(title="Size", bbox_to_anchor=(1.05, 1), loc="upper left")
    # plt.grid(True)

    # Show the plot
    plt.savefig(f"Image_Size_Hourly_outliers{includeOutliers}.png")
    plt.tight_layout()  # Adjust the padding between and around subplots to ensure nothing is cut off
    plt.show()


def plot_day_hour_comparison(cold_data, includeOutliers=True):
    if not includeOutliers:
        cold_data = remove_outliers(cold_data, "waiting_ms", THRESHOLD)

    # Convert the 'start' column to datetime format
    cold_data["start"] = pd.to_datetime(cold_data["start"])

    # Extract the hour and day from the 'start' timestamp
    cold_data["hour"] = cold_data["start"].dt.hour
    cold_data["day"] = cold_data["start"].dt.date

    # Print statistics as before (optional)

    # Create a FacetGrid to compare across days and hours
    g = sns.FacetGrid(
        cold_data, col="day", hue="size", col_wrap=4, height=4, aspect=1.5
    )
    g.map(
        sns.lineplot,
        "hour",
        "waiting_ms",
        marker="o",
        estimator=np.median,
        errorbar="ci",
    )

    # Adjust the grid
    g.add_legend(title="Size")
    g.set_axis_labels("Hour of the Day", "Waiting Time (ms)")
    g.set_titles("{col_name}")
    plt.subplots_adjust(top=0.9)
    g.fig.suptitle("Cold Start Latency by Hour and Size across Different Days")

    # Show the plot
    plt.savefig(f"Image_Size_Hourly_PerDay_outliers{includeOutliers}.png")
    plt.show()


def plot_viol(cold_data, includeOutliers=True, dayFilter=None, onlyDay=None):
    if not includeOutliers:
        cold_data = remove_outliers(cold_data, "waiting_ms", THRESHOLD)
    if dayFilter is not None:
        # Convert the 'start' column to datetime format
        cold_data["start"] = pd.to_datetime(cold_data["start"])

        # Extract the hour and day from the 'start' timestamp
        # cold_data["hour"] = cold_data["start"].dt.hour
        cold_data["day"] = cold_data["start"].dt.date
        for day in dayFilter:
            cold_data = cold_data[cold_data["day"] != day]
    if onlyDay is not None:
        # Convert the 'start' column to datetime format
        cold_data["start"] = pd.to_datetime(cold_data["start"])

        # Extract the hour and day from the 'start' timestamp
        # cold_data["hour"] = cold_data["start"].dt.hour
        cold_data["day"] = cold_data["start"].dt.date
        # debug print
        # print(cold_data["day"].unique())
        cold_data = cold_data[cold_data["day"] == onlyDay]
    # filer for flyio
    cold_data = cold_data[cold_data["provider"] == "flyio"]
    # take out size = 100
    cold_data = cold_data[cold_data["size"] != 100]

    # debug print n (amt of observations) for each size
    a = {}
    for h in cold_data["size"]:
        if a.get(h) is None:
            a[h] = 1
        else:
            a[h] += 1
    print(a)

    sns.violinplot(cold_data, x="size", y="waiting_ms")
    plt.title("Latency Distribution for flyio")
    plt.xlabel("File Size MB")
    plt.ylabel("Latency (ms)")
    plt.savefig(f"fly_coldstarts_size_outliers{includeOutliers}.png")
    plt.show()


def table_latency(data, cold):
    data["waiting_ms"] = pd.to_numeric(data["waiting_ms"], errors="coerce")

    cold_latency = (
        data[(data["isCold"] == cold)]
        .groupby(["provider", "size"])["waiting_ms"]
        .agg(
            [
                ("count", "count"),
                ("mean", lambda x: round(np.mean(x), 2)),
                ("std", lambda x: round(np.std(x), 2)),
                ("min", lambda x: round(np.min(x), 2)),
                ("p50", lambda x: round(np.percentile(x, 50), 2)),
                ("p99", lambda x: round(np.percentile(x, 99), 2)),
                ("max", lambda x: round(np.max(x), 2)),
            ]
        )
        .reset_index()
    )
    return cold_latency


def table_latency_perday(data):
    data["waiting_ms"] = pd.to_numeric(data["waiting_ms"], errors="coerce")
    # Convert the 'start' column to datetime format
    data["start"] = pd.to_datetime(data["start"])
    data["day"] = data["start"].dt.date
    cold_latency = (
        data[(data["isCold"] == 1)]
        .groupby(["provider", "size", "day"])["waiting_ms"]
        .agg(
            [
                ("count", "count"),
                ("mean", lambda x: round(np.mean(x), 2)),
                ("std", lambda x: round(np.std(x), 2)),
                ("min", lambda x: round(np.min(x), 2)),
                ("p50", lambda x: round(np.percentile(x, 50), 2)),
                ("p99", lambda x: round(np.percentile(x, 99), 2)),
                ("max", lambda x: round(np.max(x), 2)),
            ]
        )
        .reset_index()
    )
    return cold_latency


# warning: this will take a long time to run
# plot_day_hour_comparison(cold_data, includeOutliers=True)
# plot_day_hour_comparison(cold_data, includeOutliers=False)

"""
plot_boxplot(cold_data)
plot_cdf(cold_data)

plot_scatter(cold_data)
"""
# plot_day(cold_data, includeOutliers=True)
plot_day(cold_data, includeOutliers=True)

# table_latency(cold_data, True).to_csv("tables/coldsize_latency.csv")
table_latency_perday(cold_data).to_csv("tables/coldsize_latency_perday.csv")
# plot_viol(cold_data, includeOutliers=True)
from datetime import date

# print(pd.to_datetime("2024-08-23"))
# plot_viol(cold_data, includeOutliers=True, onlyDay=date(2024, 8, 22))
