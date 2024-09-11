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

INLINE_PALETTE = {
    "aws": "#dbd642",
    "google": "#374fd4",
    "flyio": "#6f32a8",
    "cloudflare-HTTP": "orange",
    "cloudflare-RPC": "black",
}


def plot_inline_data_latency_boxplot(
    data, includeColdStarts, includeOutliers, quantile=50
):
    if not includeColdStarts:
        data = data[data["isConsumerCold"] == 0]

    if not includeOutliers:
        data = remove_outliers(data, "transfer_latency", THRESHOLD)

    # Convert payload_size to numeric values
    data["payload_size"] = pd.to_numeric(data["payload_size"], errors="coerce")

    # Filter for cold starts if needed
    data = data[data["status"] == 200]

    # Filter for specific payload sizes
    payload_sizes = [512, 1023, 2048, 8192]
    data = data[data["payload_size"].isin(payload_sizes)]

    # Divide Cloudflare into Cloudflare-Http and Cloudflare-RPC depending on the URL
    data.loc[data["provider"] == "cloudflare", "provider"] = data.loc[
        data["provider"] == "cloudflare", "consumer_url"
    ].apply(lambda x: "cloudflare-HTTP" if "consumer-http" in x else "cloudflare-RPC")

    s = sns.violinplot(
        x="payload_size",
        y="transfer_latency",
        hue="provider",
        data=data,
        palette=INLINE_PALETTE,
        fill=True,
        # inner=None,
    )

    plt.grid()
    plt.title(
        f"Data Transfer Latency by Payload Size and Provider | outliers: {includeOutliers} | cold starts: {includeColdStarts}"
    )
    plt.xlabel("Payload Size (KB)")
    plt.ylabel("Transfer Latency (ms)")
    # plt.yscale("log")
    plt.ylim(0, 600)
    sns.move_legend(s, "upper left", bbox_to_anchor=(1, 1))
    plt.savefig(f"inline_data_latency_violinplot_outliers{includeOutliers}.png")
    plt.show()


def get_quantile_latency(data, provider, payloadSize, quantile):
    # Filter for the specific provider and payload size
    filtered_data = data[
        (data["provider"] == provider) & (data["payload_size"] == payloadSize)
    ]
    if len(filtered_data) == 0:
        return None
    # Compute the quantile latency
    quantile_latency = filtered_data["transfer_latency"].quantile(quantile / 100)

    return quantile_latency


def get_std_dev_latency(data, provider, payloadSize):
    # Filter for the specific provider and payload size
    filtered_data = data[
        (data["provider"] == provider) & (data["payload_size"] == payloadSize)
    ]
    # Compute the standard deviation of latency
    if len(filtered_data) == 0:
        return None
    std_dev_latency = filtered_data["transfer_latency"].std()

    return std_dev_latency


# returns a table with the median and 99th percentile latency for each provider and payload size
def build_table(data):
    payload_sizes = [512, 1023, 2048, 8192]

    # Divide Cloudflare into Cloudflare-Http and Cloudflare-RPC depending on the URL
    data.loc[data["provider"] == "cloudflare", "provider"] = data.loc[
        data["provider"] == "cloudflare", "consumer_url"
    ].apply(lambda x: "cloudflare-HTTP" if "consumer-http" in x else "cloudflare-RPC")
    providers = data["provider"].unique()
    table = []
    data = data[data["status"] == 200]
    for provider in providers:
        for payload_size in payload_sizes:

            median_latency = get_quantile_latency(data, provider, payload_size, 50)
            percentile_99 = get_quantile_latency(data, provider, payload_size, 99)
            std_dev_latency = get_std_dev_latency(data, provider, payload_size)
            if median_latency is not None:
                median_latency = int(median_latency)
            if percentile_99 is not None:
                percentile_99 = int(percentile_99)
            if std_dev_latency is not None:
                std_dev_latency = int(std_dev_latency)
            table.append(
                {
                    "provider": provider,
                    "payloadSize (KB)": payload_size,
                    "median": median_latency,
                    "tail": percentile_99,
                    "std": std_dev_latency,
                }
            )

    table = pd.DataFrame(
        table,
        columns=[
            "provider",
            "payloadSize (KB)",
            "median",
            "tail",
            "std",
        ],
    )
    table.to_csv("inline_data_latency_table.csv", index=False)
    table.to_excel("inline_data_latency_table.xlsx", index=False)
    return table


def plot_hist_together(data, includeColdStarts, includeOutliers):
    # Filter for specific payload sizes
    payload_sizes = [512, 1023, 2048, 8192]
    data = data[data["payload_size"].isin(payload_sizes)]

    # Divide Cloudflare into Cloudflare-Http and Cloudflare-RPC depending on the URL
    data.loc[data["provider"] == "cloudflare", "provider"] = data.loc[
        data["provider"] == "cloudflare", "consumer_url"
    ].apply(lambda x: "cloudflare-HTTP" if "consumer-http" in x else "cloudflare-RPC")

    sns.kdeplot(
        data,
        x="transfer_latency",
        hue="provider",
        palette=INLINE_PALETTE,
    )

    plt.grid()
    plt.title(
        f"Data Transfer Latency by Payload Size and Provider | outliers: {includeOutliers} | cold starts: {includeColdStarts}"
    )
    plt.xlabel("Transfer Latency (ms)")
    plt.ylabel("Frequency")
    # plt.savefig(f"inline_data_latency_histplot_outliers{includeOutliers}.png")
    plt.show()


def plot_v2(data, includeColdStarts, includeOutliers, quantile=50):
    if not includeColdStarts:
        data = data[data["isConsumerCold"] == 0]

    if not includeOutliers:
        data = remove_outliers(data, "transfer_latency", THRESHOLD)

    # Convert payload_size to numeric values
    data["payload_size"] = pd.to_numeric(data["payload_size"], errors="coerce")

    # Filter for cold starts if needed
    data = data[data["status"] == 200]

    # Filter for specific payload sizes
    payload_sizes = [512, 1023, 2048, 8192]
    data = data[data["payload_size"].isin(payload_sizes)]

    # Divide Cloudflare into Cloudflare-Http and Cloudflare-RPC depending on the URL
    data.loc[data["provider"] == "cloudflare", "provider"] = data.loc[
        data["provider"] == "cloudflare", "consumer_url"
    ].apply(lambda x: "cloudflare-HTTP" if "consumer-http" in x else "cloudflare-RPC")

    # Create the violin plot
    plt.figure(figsize=(12, 6))
    s = sns.violinplot(
        x="payload_size",
        y="transfer_latency",
        hue="provider",
        data=data,
        palette=INLINE_PALETTE,
        fill=True,
        cut=0,
        scale="width",
    )

    # Calculate medians for each provider and payload size
    medians = (
        data.groupby(["provider", "payload_size"])["transfer_latency"]
        .median()
        .unstack()
    )

    # Add lines connecting medians
    for provider in medians.index:
        provider_medians = medians.loc[provider]
        plt.plot(
            range(len(payload_sizes)),
            provider_medians,
            marker="o",
            linestyle="-",
            label=f"{provider} median",
        )

    plt.grid(True, axis="y", linestyle="--", alpha=0.7)
    plt.title(
        f"Data Transfer Latency by Payload Size and Provider\nOutliers: {'Included' if includeOutliers else 'Excluded'} | Cold Starts: {'Included' if includeColdStarts else 'Excluded'}"
    )
    plt.xlabel("Payload Size (KB)")
    plt.ylabel("Transfer Latency (ms)")
    plt.ylim(0, 600)
    plt.xticks(range(len(payload_sizes)), payload_sizes)

    # Adjust legend
    handles, labels = plt.gca().get_legend_handles_labels()
    violin_handles = handles[: len(set(data["provider"]))]
    line_handles = handles[len(set(data["provider"])) :]
    plt.legend(
        violin_handles + line_handles,
        [label for label in labels if "median" not in label]
        + [f"{label} median" for label in labels if "median" not in label],
        bbox_to_anchor=(1.05, 1),
        loc="upper left",
    )

    plt.tight_layout()
    plt.show()


data = get_data("InlineData")
data = data[data["isConsumerCold"] == 0]
# Convert timestamps to numeric values (in milliseconds)
data["producerTimestamp"] = pd.to_numeric(data["producerTimestamp"], errors="coerce")
data["consumerReceivedTimestamp"] = pd.to_numeric(
    data["consumerReceivedTimestamp"], errors="coerce"
)


# Compute the transfer latency
data["transfer_latency"] = data["consumerReceivedTimestamp"] - data["producerTimestamp"]
# Convert payload_size to numeric values
data["payload_size"] = pd.to_numeric(data["payload_size"], errors="coerce")


def main():

    print(get_std_dev_latency(data, "aws", 1023))
    print(get_quantile_latency(data, "aws", 512, 50))

    build_table(data)

    plot_hist_together(data, False, True)
    plot_hist_together(data, False, True)


plot_inline_data_latency_boxplot(data, False, True, 50)
plot_v2(data, False, True, 50)
