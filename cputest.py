from overview import *

# Load the data from CpuTest table
data = get_data("CpuTest")

# Filter data to filter out cold starts (isCold == 0)
cold_data = data[data["isCold"] == 0]


# Boxplot of Latency (waiting_ms) by Fibonacci number (n)
def plot_latency_boxplot(cold_data):
    plt.figure(figsize=(12, 8))
    sns.boxplot(
        x="n",
        y="waiting_ms",
        data=cold_data,
        palette="magma",
    )
    plt.title("Cold Start Latency (waiting_ms) by Fibonacci Number")
    plt.xlabel("Fibonacci Number (n)")
    plt.ylabel("Latency (ms)")
    plt.yscale("log")
    plt.xticks(rotation=45, ha="right")  # Rotate x-axis labels for better readability
    plt.savefig("cpu_latency_boxplot.png")
    plt.show()


# Boxplot of Fibonacci Duration (fibDuration) by Fibonacci number (n)
def plot_fibduration_boxplot(cold_data):
    plt.figure(figsize=(12, 8))
    sns.boxplot(
        x="n",
        y="fibDuration",
        data=cold_data,
        palette="viridis",
    )
    plt.title("Fibonacci Calculation Duration by Fibonacci Number")
    plt.xlabel("Fibonacci Number (n)")
    plt.ylabel("Duration (ms)")
    plt.yscale("log")
    plt.xticks(rotation=45, ha="right")  # Rotate x-axis labels for better readability
    plt.savefig("cpu_fibduration_boxplot.png")
    plt.show()


# Plotting CDF for the waiting_ms (latency)
def plot_latency_cdf(cold_data):
    plt.figure(figsize=(10, 6))
    plt.title("CDF of Cold Start Latency")

    sorted_latency = np.sort(cold_data["waiting_ms"])
    yvals = np.arange(1, len(sorted_latency) + 1) / float(len(sorted_latency))

    sns.ecdfplot(cold_data["waiting_ms"], label="CDF", color="blue")

    plt.xscale("log")
    plt.xlabel("Latency (ms)")
    plt.ylabel("ECDF")
    plt.legend()
    plt.savefig("cdf_latency_cpu.png")
    plt.show()


# Plotting CDF for the fibDuration
def plot_fibduration_cdf(cold_data):
    plt.figure(figsize=(10, 6))
    plt.title("CDF of Fibonacci Calculation Duration")

    sorted_duration = np.sort(cold_data["fibDuration"])
    yvals = np.arange(1, len(sorted_duration) + 1) / float(len(sorted_duration))

    sns.ecdfplot(cold_data["fibDuration"], label="CDF", color="green")

    plt.xscale("log")
    plt.xlabel("Duration (ms)")
    plt.ylabel("ECDF")
    plt.legend()
    plt.savefig("cdf_fibduration_cpu.png")
    plt.show()


def plot_latency_vs_fibduration(cold_data):
    plt.figure(figsize=(10, 6))
    sns.scatterplot(
        x="waiting_ms",
        y="fibDuration",
        hue="n",  # Optional: Color by Fibonacci number
        data=cold_data,
        palette="plasma",
        edgecolor=None,
    )
    plt.title("Relationship Between Cold Start Latency and Fibonacci Duration")
    plt.xlabel("Latency (ms)")
    plt.ylabel("Fibonacci Calculation Duration (ms)")
    plt.xscale("log")
    plt.yscale("log")
    plt.savefig("latency_vs_fibduration.png")
    plt.show()


plot_latency_boxplot(cold_data)
plot_fibduration_boxplot(cold_data)
plot_latency_cdf(cold_data)
plot_fibduration_cdf(cold_data)
plot_latency_vs_fibduration(cold_data)
