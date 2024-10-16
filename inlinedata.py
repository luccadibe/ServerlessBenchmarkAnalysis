from overview import *
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np


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

    data = data[data["status"] == 200]

    # Filter for specific payload sizes
    payload_sizes = [512, 1023, 2048, 8192]
    data = data[data["payload_size"].isin(payload_sizes)]

    # Divide Cloudflare into Cloudflare-Http and Cloudflare-RPC depending on the URL
    # data.loc[data["provider"] == "cloudflare", "provider"] = data.loc[data["provider"] == "cloudflare", "consumer_url"].apply(lambda x: "cloudflare-HTTP" if "consumer-http" in x else "cloudflare-RPC")

    s = sns.boxplot(
        x="payload_size",
        y="transfer_latency",
        hue="provider",
        data=data,
        palette=INLINE_PALETTE,
        fill=True,
        # inner=None,
    )
    # plt.title(f"Data Transfer Latency by Payload Size and Provider")
    plt.xlabel("Payload Size (KB)")
    plt.ylabel("Transfer Latency (ms)")
    plt.yscale("log")
    # plt.ylim(0, 600)
    sns.move_legend(s, "upper left", bbox_to_anchor=(1, 1))
    plt.savefig(f"pdf/data_transfer/inline_data_latency.pdf")
    plt.show()


def boxplot_w_facet(data):
    # Convert payload_size to numeric values
    data["payload_size"] = pd.to_numeric(data["payload_size"], errors="coerce")

    data = data[data["status"] == 200]

    # Filter for specific payload sizes
    payload_sizes = [512, 1023, 2048, 8192]
    data = data[data["payload_size"].isin(payload_sizes)]
    # Divide Cloudflare into Cloudflare-Http and Cloudflare-RPC depending on the URL
    data.loc[data["provider"] == "cloudflare", "provider"] = data.loc[
        data["provider"] == "cloudflare", "consumer_url"
    ].apply(lambda x: "cloudflare-HTTP" if "consumer-http" in x else "cloudflare-RPC")

    g = sns.FacetGrid(
        data,
        col="provider",
        hue="payload_size",
        col_wrap=2,
        height=4,
        aspect=1.5,
        sharex=True,
    )

    g.map(
        sns.boxplot,
        data=data,
        x="payload_size",
        y="transfer_latency",
        hue="provider",
        palette=INLINE_PALETTE,
    )
    # add connection lines for medians

    plt.title(f"Data Transfer Latency by Payload Size and Provider")
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
    s = sns.boxplot(
        x="payload_size",
        y="transfer_latency",
        hue="provider",
        data=data,
        palette=INLINE_PALETTE,
        fill=True,
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
    plt.ylim(0, 2000)
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


def table_datatransfer(data):
    data = data[data["status"] == 200]
    data["payload_size"] = pd.to_numeric(data["payload_size"], errors="coerce")
    data = data[data["payload_size"].isin([512, 1023, 2048, 8192])]
    data.loc[data["provider"] == "cloudflare", "provider"] = data.loc[
        data["provider"] == "cloudflare", "consumer_url"
    ].apply(lambda x: "cloudflare-HTTP" if "consumer-http" in x else "cloudflare-RPC")
    return (
        data.groupby(["provider", "payload_size"])["transfer_latency"]
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


def preprocess_data(data, include_cold_starts=False, include_outliers=True):
    if not include_cold_starts:
        data = data[data["isConsumerCold"] == 0]

    if not include_outliers:
        data = remove_outliers(data, "transfer_latency", THRESHOLD)

    data["payload_size"] = pd.to_numeric(data["payload_size"], errors="coerce")
    data = data[data["status"] == 200]

    payload_sizes = [512, 1023, 2048, 8192]
    data = data[data["payload_size"].isin(payload_sizes)]

    data.loc[data["provider"] == "cloudflare", "provider"] = data.loc[
        data["provider"] == "cloudflare", "consumer_url"
    ].apply(lambda x: "cloudflare-HTTP" if "consumer-http" in x else "cloudflare-RPC")

    return data

def plot_latency_boxplot_with_median_lines(data, include_cold_starts=False, include_outliers=True):
    data = preprocess_data(data, include_cold_starts, include_outliers)

    # Create boxplot
    sns.boxplot(
        x="payload_size",
        y="transfer_latency",
        hue="provider",
        data=data,
        palette=INLINE_PALETTE,
        width=0.8,
        fliersize=2,
    )

    # Calculate medians for each provider and payload size
    medians = data.groupby(["provider", "payload_size"])["transfer_latency"].median().unstack()

    # Add lines connecting medians
    providers = data['provider'].unique()
    num_payload_sizes = len(data['payload_size'].unique())
    width = 0.8 / len(providers)
    
    for i, provider in enumerate(providers):
        if provider in medians.index:
            provider_medians = medians.loc[provider]
            x_positions = np.arange(num_payload_sizes) + (i - len(providers)/2 + 0.5) * width
            plt.plot(x_positions, provider_medians, marker="o", linestyle="-", color=INLINE_PALETTE[provider], label=f"{provider} median")

    plt.grid(True, axis="y", linestyle="--", alpha=0.7)
    plt.xlabel("Payload Size (KB)")
    plt.ylabel("Transfer Latency (ms)")
    plt.yscale("log")
    plt.xticks(range(num_payload_sizes), sorted(data['payload_size'].unique()))

    # Adjust legend
    handles, labels = plt.gca().get_legend_handles_labels()
    plt.legend(handles[:len(providers)], labels[:len(providers)], title="Provider")
    plt.savefig(f"pdf/data_transfer/inline_data_latency_median_lines.pdf")
    plt.show()

def main():
    data = get_data("InlineData")
    data["transfer_latency"] = pd.to_numeric(data["consumerReceivedTimestamp"], errors="coerce") - pd.to_numeric(data["producerTimestamp"], errors="coerce")
    data["payload_size"] = pd.to_numeric(data["payload_size"], errors="coerce")

    # Remove data for cloudflare (not needed as their transfer latency is 0)
    data = data[data["provider"] != "cloudflare"]

    #plot_latency_boxplot_with_median_lines(data)
    build_table(data)

if __name__ == "__main__":
    main()