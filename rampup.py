from overview import *

# timestamp format
# 2024-08-02T11:33:22.566Z
pd.set_option("display.max_colwidth", None)
"""
Table: RampUp
    cid          name     type  notnull dflt_value  pk
0     0            id  INTEGER        0       None   1
1     1         start     TEXT        0       None   0
2     2           end     TEXT        0       None   0
3     3    sending_ms     REAL        0       None   0
4     4    waiting_ms     REAL        0       None   0
5     5  receiving_ms     REAL        0       None   0
6     6      total_ms     REAL        0       None   0
7     7        status  INTEGER        0       None   0
8     8          body     TEXT        0       None   0
9     9        isCold  BOOLEAN        0       None   0
10   10      provider     TEXT        0       None   0
11   11           url     TEXT        0       None   0
12   12       test_id     TEXT        0       None   0
"""


#  identify the runtime based on the URL
def identify_runtime(row):
    if row["provider"] == "aws":
        if "iohfkcvlai3qjizwfvbpiv257y0kntcw" in row["url"]:
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


def rampup(rampup_data, includeColdStarts, includeOutliers, runtime, quantile=50):
    if not includeColdStarts:
        rampup_data = rampup_data[rampup_data["isCold"] == 0]
    if not includeOutliers:
        rampup_data = remove_outliers(rampup_data, "waiting_ms", THRESHOLD)
    rampup_data["second"] = pd.to_numeric(rampup_data["second"], errors="coerce")
    rampup_data["waiting_ms"] = pd.to_numeric(
        rampup_data["waiting_ms"], errors="coerce"
    )
    rampup_data = rampup_data[rampup_data["runtime"] == runtime]

    #  quantile for each second and provider
    grouped_data = (
        rampup_data.groupby(["second", "provider"])["waiting_ms"]
        .quantile(quantile / 100)
        .reset_index()
    )
    plt.figure(figsize=(14, 7))
    sns.lineplot(
        x="second",
        y="waiting_ms",
        hue="provider",
        data=grouped_data,
        palette=PALETTE,
        marker="o",
    )

    plt.title(f"")
    plt.xlabel("Time Elapsed (seconds)")
    plt.ylabel(f"Latency (ms) - {quantile}th Percentile")
    plt.xticks(range(25))
    plt.axvline(x=18, color="red", linestyle="--", label="Ramp Up Complete")
    plt.axvline(x=20, color="orange", linestyle="--", label="Cooldown")
    plt.legend(title="Provider")
    plt.savefig(f"pdf/rampup/rampup_runtime{runtime}_{quantile}.pdf")
    plt.show()


def plot_rampup_fly_nodevsgo(data, quantile=50):
    data["second"] = pd.to_numeric(data["second"], errors="coerce")
    data["waiting_ms"] = pd.to_numeric(data["waiting_ms"], errors="coerce")
    data = data[data["provider"] == "flyio"]
    #  quantile for each second and provider
    grouped_data = (
        data.groupby(["second", "provider", "runtime"])["waiting_ms"]
        .quantile(quantile / 100)
        .reset_index()
    )
    sns.lineplot(
        x="second",
        y="waiting_ms",
        hue="runtime",
        data=grouped_data,
        palette={"Golang": "blue", "Node.js": "green"},
        marker="o",
        estimator=np.median,
    )
    plt.title("")
    plt.xlabel("Time Elapsed (seconds)")
    plt.ylabel("Latency (ms)")
    plt.xticks(range(25))
    plt.axvline(x=18, color="red", linestyle="--", label="Ramp Up Complete")
    plt.axvline(x=20, color="orange", linestyle="--", label="Cooldown")
    plt.legend(title="Runtime")
    plt.savefig(f"pdf/rampup/rampup_fly_govsnode_{quantile}.pdf")
    plt.show()


def table_latency(data):
    data["waiting_ms"] = pd.to_numeric(data["waiting_ms"], errors="coerce")
    data["second"] = pd.to_numeric(data["second"], errors="coerce")
    data["isCold"] = data["isCold"].astype(int)  # Ensure isCold is numeric
    
    # First, calculate the sum of cold starts for each (test_id, provider, runtime, second)
    cold_starts_per_test = data.groupby(["test_id", "provider", "runtime", "second"])["isCold"].sum().reset_index()
    
    # Then, calculate the average of these sums across test_ids
    cold_latency = (
        data
        .groupby(["provider", "runtime", "second"])
        .agg(
            count=("waiting_ms", "count"),
            mean=("waiting_ms", lambda x: round(np.mean(x), 2)),
            std=("waiting_ms", lambda x: round(np.std(x), 2)),
            min=("waiting_ms", lambda x: round(np.min(x), 2)),
            p50=("waiting_ms", lambda x: round(np.percentile(x, 50), 2)),
            p99=("waiting_ms", lambda x: round(np.percentile(x, 99), 2)),
            max=("waiting_ms", lambda x: round(np.max(x), 2)),
        )
        .reset_index()
    )
    
    # Merge the average cold starts
    cold_starts_avg = cold_starts_per_test.groupby(["provider", "runtime", "second"])["isCold"].mean().reset_index()
    cold_latency = cold_latency.merge(cold_starts_avg, on=["provider", "runtime", "second"], suffixes=('', '_avg'))
    cold_latency = cold_latency.rename(columns={"isCold": "avg_cold_starts"})
    
    return cold_latency

def table_latency_first_three_seconds(data):
    data["waiting_ms"] = pd.to_numeric(data["waiting_ms"], errors="coerce")
    data["second"] = pd.to_numeric(data["second"], errors="coerce")
    data["isCold"] = data["isCold"].astype(int)  # Ensure isCold is numeric
    
    # Filter for first three seconds
    data_first_three = data[data["second"].isin([0, 1, 2])]
    
    # First, calculate the sum of cold starts for each (test_id, provider, runtime)
    cold_starts_per_test = data_first_three.groupby(["test_id", "provider", "runtime"])["isCold"].sum().reset_index()
    
    # Then, calculate the average of these sums across test_ids
    cold_latency = (
        data_first_three
        .groupby(["provider", "runtime"])
        .agg(
            count=("waiting_ms", "count"),
            mean=("waiting_ms", lambda x: round(np.mean(x), 2)),
            std=("waiting_ms", lambda x: round(np.std(x), 2)),
            min=("waiting_ms", lambda x: round(np.min(x), 2)),
            p50=("waiting_ms", lambda x: round(np.percentile(x, 50), 2)),
            p99=("waiting_ms", lambda x: round(np.percentile(x, 99), 2)),
            max=("waiting_ms", lambda x: round(np.max(x), 2)),
        )
        .reset_index()
    )
    
    # Merge the average cold starts
    cold_starts_avg = cold_starts_per_test.groupby(["provider", "runtime"])["isCold"].mean().reset_index()
    cold_latency = cold_latency.merge(cold_starts_avg, on=["provider", "runtime"], suffixes=('', '_avg'))
    cold_latency = cold_latency.rename(columns={"isCold": "avg_cold_starts"})
    
    return cold_latency


with open("rampupQuery.sql", "r") as file:
    q = file.read()
    data2 = query_data("RampUp", q)
    data2["runtime"] = data2.apply(identify_runtime, axis=1)

    table_latency(data2).to_csv("tables/rampup_latency.csv", index=False)
    table_latency_first_three_seconds(data2).to_csv("tables/rampup_latency_first_three_seconds.csv", index=False)

    
    rampup(data2, True, True, "Node.js", 50)
    rampup(data2, True, True, "Node.js", 99)

    rampup(data2, True, True, "Python", 50)
    rampup(data2, True, True, "Python", 99)

    # TODO fix this fucking bug!!!!!!
    data2 = data2[data2["provider"] == "flyio"]
    # only include runtimes where provider is flyio
    data2 = data2[data2["runtime"].isin(["Node.js", "Golang"])]

    plot_rampup_fly_nodevsgo(data2, 50)
    plot_rampup_fly_nodevsgo(data2, 99)
    


# print_headers()

