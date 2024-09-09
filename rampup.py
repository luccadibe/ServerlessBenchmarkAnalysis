from overview import *
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

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


def rampup(rampup_data, includeColdStarts, includeOutliers, quantile=50):
    if not includeColdStarts:
        rampup_data = rampup_data[rampup_data["isCold"] == 0]
    if not includeOutliers:
        rampup_data = remove_outliers(rampup_data, "waiting_ms", THRESHOLD)
    rampup_data["second"] = pd.to_numeric(rampup_data["second"], errors="coerce")
    rampup_data["waiting_ms"] = pd.to_numeric(
        rampup_data["waiting_ms"], errors="coerce"
    )

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

    plt.title(
        f"Latency (Quantile: {quantile}%) by Provider | outliers: {includeOutliers} | cold starts: {includeColdStarts}"
    )
    plt.xlabel("Time Elapsed (seconds)")
    plt.ylabel(f"Latency (ms) - {quantile}th Percentile")
    plt.xticks(range(25))
    plt.axvline(x=18, color="red", linestyle="--", label="Ramp Up Complete")
    plt.axvline(x=20, color="orange", linestyle="--", label="Cooldown")
    plt.legend(title="Provider")
    plt.savefig(f"rampup_{quantile}.png")
    plt.show()


data = get_data("RampUp")


with open("rampupQuery.sql", "r") as file:
    q = file.read()
    data2 = query_data("RampUp", q)
    rampup(data2, True, True, 50)
    rampup(data2, True, True, 99)

# print_headers()
