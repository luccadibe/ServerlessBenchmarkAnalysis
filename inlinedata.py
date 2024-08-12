from overview import *
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


# table format

"""
Table: InlineData
    cid                       name     type  notnull dflt_value  pk     
0     0                         id  INTEGER        0       None   1     
1     1                      start     TEXT        0       None   0     
2     2                        end     TEXT        0       None   0     
3     3          producerTimestamp     TEXT        0       None   0     
4     4  consumerReceivedTimestamp     TEXT        0       None   0     
5     5             isConsumerCold  BOOLEAN        0       None   0     
6     6                     status  INTEGER        0       None   0     
7     7                   provider     TEXT        0       None   0     
8     8                        url     TEXT        0       None   0     
9     9               payload_size     TEXT        0       None   0     
10   10               consumer_url     TEXT        0       None   0
"""


def plot_inline_data_latency_boxplot(
    data, includeColdStarts, includeOutliers, quantile=50
):
    if not includeColdStarts:
        data = data[data["isConsumerCold"] == 0]

    # Convert timestamps to numeric values (in milliseconds)
    data["producerTimestamp"] = pd.to_numeric(
        data["producerTimestamp"], errors="coerce"
    )
    data["consumerReceivedTimestamp"] = pd.to_numeric(
        data["consumerReceivedTimestamp"], errors="coerce"
    )

    # Compute the transfer latency
    data["transfer_latency"] = (
        data["consumerReceivedTimestamp"] - data["producerTimestamp"]
    )

    if not includeOutliers:
        data = remove_outliers(data, "transfer_latency", THRESHOLD)

    # Convert payload_size to numeric values
    data["payload_size"] = pd.to_numeric(data["payload_size"], errors="coerce")

    # Filter for cold starts if needed
    data = data[data["isConsumerCold"] == 0]

    # Filter for specific payload sizes
    payload_sizes = [512, 1023, 2048, 8192]
    data = data[data["payload_size"].isin(payload_sizes)]

    # Create the boxplot
    plt.figure(figsize=(14, 7))

    sns.boxplot(
        x="payload_size",
        y="transfer_latency",
        hue="provider",
        data=data,
        palette=PALETTE,
    )

    plt.title(
        f"Transfer Latency by Payload Size and Consumer URL | outliers: {includeOutliers} | cold starts: {includeColdStarts}"
    )
    plt.xlabel("Payload Size (bytes)")
    plt.ylabel("Transfer Latency (ms)")
    plt.legend(title="Consumer URL")
    plt.grid(True)
    plt.savefig("inline_latency_boxplot.png")
    plt.show()


data = get_data("InlineData")
plot_inline_data_latency_boxplot(data, False, False, 50)
