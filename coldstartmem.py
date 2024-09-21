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

    """
    print(
        cold_data.groupby(["memory", "provider"])["waiting_ms"].agg(
            ["max", "min", "median"]
        )
    )
    """
    # g = sns.FacetGrid(cold_data, col="provider", palette=PALETTE)
    # g.map(sns.boxplot, data=cold_data, x="memory", y="waiting_ms")
    sns.boxplot(
        data=cold_data,
        x="memory",
        y="waiting_ms",
        hue="provider",
        palette=PALETTE,
        legend=False,
    )
    plt.ylim(0, 2000)
    plt.title("")
    plt.xlabel("Memory Configuration (MB)")
    plt.ylabel("Latency (ms)")
    # g.set_titles("{col_name}")
    # g.set_xlabels("Memory Allocation (MB)")
    # g.set_ylabels("Latency (ms)")
    plt.savefig(
        f"pdf/cold_start_memory/coldstarts_memory_boxplot_grid_outliers{includeOutliers}.pdf"
    )
    plt.show()


# Plotting ECDF for the waiting_ms (latency)
# Every line should represent a different memory allocation
# one column for each provider, only one row
def plot_cdf(cold_data):
    g = sns.FacetGrid(cold_data, col="provider", row="memory", margin_titles=True)

    g.map_dataframe(sns.ecdfplot, "waiting_ms", hue="provider", palette=PALETTE)
    plt.xlim(0, 2000)
    for ax in g.axes.flat:
        ax.set_ylabel("ECDF")
        ax.set_xlabel("Latency (ms)")
    g.add_legend()
    plt.savefig("pdf/cold_start_memory/coldstarts_memory_ecdf.pdf")
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


def print_stats(cold_data):
    # print median and tail latency and std deviation for each provider and memory config
    print(
        cold_data.groupby(["provider", "memory"])["waiting_ms"].agg(
            ["median", "std", lambda x: np.percentile(x, 99)]
        )
    )


# plot_boxplot(cold_data)
# plot_cdf(cold_data, includeOutliers=False)
plot_boxplot_grid(cold_data, includeOutliers=True)
plot_cdf(cold_data)
# plot_distribution(cold_data, "flyio", 1024, includeOutliers=True)

# print_stats(cold_data)
