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


with open("rampupQuery.sql", "r") as file:
    q = file.read()
    data2 = query_data("RampUp", q)
    data2["runtime"] = data2.apply(identify_runtime, axis=1)

    rampup(data2, True, True, "Node.js", 50)
    rampup(data2, True, True, "Node.js", 99)

    rampup(data2, True, True, "Python", 50)
    rampup(data2, True, True, "Python", 99)

    plot_rampup_fly_nodevsgo(data2, 50)
    plot_rampup_fly_nodevsgo(data2, 99)


# print_headers()
