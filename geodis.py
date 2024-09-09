from overview import PALETTE, THRESHOLD, get_data, remove_outliers
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

#      Table: GeoDis
"""     cid          name     type  notnull dflt_value  pk
0     0            id  INTEGER        0       None   1
1     1         start     TEXT        0       None   0
2     2           end     TEXT        0       None   0
3     3    sending_ms     REAL        0       None   0
4     4    waiting_ms     REAL        0       None   0
5     5  receiving_ms     REAL        0       None   0
6     6      total_ms     REAL        0       None   0
7     7        status  INTEGER        0       None   0
8     8          body     TEXT        0       None   0
9     9   instance_id  INTEGER        0       None   0
10   10     load_zone     TEXT        0       None   0
11   11      provider     TEXT        0       None   0
12   12           url     TEXT        0       None   0
13   13      duration     TEXT        0       None   0
 """
# this is how the body column looks like
# {\"timestamp\":1722619893112;\"isCold\":true}


# loadzones:
"""
['amazon:au:sydney' 'amazon:br:sao paulo' 'amazon:cn:hong kong'
 'amazon:gb:london' 'amazon:in:mumbai' 'amazon:jp:tokyo' 'amazon:kr:seoul'
 'amazon:sa:cape town' 'amazon:se:stockholm' 'amazon:us:portland'  
 'amazon:ca:montreal' 'amazon:us:palo alto' 'amazon:jp:osaka'      
 'amazon:it:milan' 'amazon:sg:singapore' 'amazon:ie:dublin'        
 'amazon:de:frankfurt' 'amazon:us:columbus' 'amazon:fr:paris'      
 'amazon:us:ashburn']

"""
LOAD_ZONE_GROUP_1 = [
    "amazon:au:sydney",
    "amazon:br:sao paulo",
    "amazon:cn:hong kong",
    "amazon:gb:london",
    "amazon:in:mumbai",
    "amazon:jp:tokyo",
    "amazon:kr:seoul",
    "amazon:sa:cape town",
    "amazon:se:stockholm",
    "amazon:us:portland",
]

LOAD_ZONE_GROUP_2 = [
    "amazon:ca:montreal",
    "amazon:us:palo alto",
    "amazon:jp:osaka",
    "amazon:it:milan",
    "amazon:sg:singapore",
    "amazon:ie:dublin",
    "amazon:de:frankfurt",
    "amazon:us:columbus",
    "amazon:fr:paris",
    "amazon:us:ashburn",
]


data = get_data("GeoDis")

# Add new isCold column based on the body column
data["isCold"] = data["body"].apply(lambda x: "true" in x)

# Add the second GeoDis2 data

data2 = get_data("GeoDis2")
data2["isCold"] = data2["body"].apply(lambda x: "true" in x)

# Combine the two datasets
combinedData = pd.concat([data, data2])

# filter out the cold starts
# data = data[data["isCold"] == 0]


def plot_geodis_data(
    geodis_data, includeColdStarts, includeOutliers, plottype="bar", num=1
):
    if not includeColdStarts:
        geodis_data = geodis_data[geodis_data["isCold"] == 0]

    if not includeOutliers:
        geodis_data = remove_outliers(geodis_data, "waiting_ms", THRESHOLD)

    plt.figure(figsize=(12, 8))

    # there is 20 total different load_zones. Each starts with "amazon:" so we can strip that out

    geodis_data["load_zone"] = geodis_data["load_zone"].str.replace("amazon:", "")

    # plot the first 10 load_zones
    # compare the performance of each function per load zone
    if plottype == "bar":
        sns.barplot(
            x="load_zone",
            y="waiting_ms",
            hue="provider",
            data=geodis_data,
            palette=PALETTE,
        )
    elif plottype == "box":
        sns.boxplot(
            x="load_zone",
            y="waiting_ms",
            hue="provider",
            data=geodis_data,
            palette=PALETTE,
        )
    plt.xticks(rotation=45)
    plt.title(
        f"Latency (ms) per Load Zone | outliers: {includeOutliers} | cold starts: {includeColdStarts}"
    )
    plt.xlabel("Load Zone")
    plt.ylabel("Latency (ms)")
    plt.savefig(f"geodis{num}-{plottype}.png")
    plt.show()


# ECDF plot generalised over all load_zones
def plot_ecdf(data, includeColdStarts, includeOutliers):
    if not includeColdStarts:
        data = data[data["isCold"] == 0]

    if not includeOutliers:
        data = remove_outliers(data, "waiting_ms", THRESHOLD)

    plt.figure(figsize=(12, 8))

    for provider in data["provider"].unique():
        provider_data = data[data["provider"] == provider]
        sns.ecdfplot(data=provider_data, x="waiting_ms", label=provider)

    plt.title(
        f"ECDF of Latency (ms) | outliers: {includeOutliers} | cold starts: {includeColdStarts}"
    )
    plt.xlabel("Latency (ms)")
    plt.xscale("log")
    plt.ylabel("ECDF")
    plt.legend()

    ticks = [10, 50, 100, 250, 500, 1000, 2000]
    plt.xticks(ticks, labels=[str(tick) for tick in ticks])
    plt.savefig("geodis-ecdf.png")
    plt.show()


def plot_combined_ecdf(data, includeColdStarts, includeOutliers):
    if not includeColdStarts:
        data = data[data["isCold"] == 0]

    if not includeOutliers:
        data = remove_outliers(data, "waiting_ms", THRESHOLD)

    g = sns.FacetGrid(
        data,
        col="provider",
        hue="load_zone",
        col_wrap=2,
        height=4,
        aspect=1.5,
        sharex=True,
    )

    # Map ECDF plots to the grid
    g.map(sns.ecdfplot, "waiting_ms", complementary=False)

    # plt.title(f"ECDF of Latency (ms) | outliers: {includeOutliers} | cold starts: {includeColdStarts}")

    plt.xlabel("Latency (ms)")
    plt.ylabel("ECDF")
    plt.legend()
    plt.show()


def plot_joy(data, includeColdStarts, includeOutliers):
    if not includeColdStarts:
        data = data[data["isCold"] == 0]

    if not includeOutliers:
        data = remove_outliers(data, "waiting_ms", THRESHOLD)

    sns.set_theme(style="whitegrid")
    g = sns.FacetGrid(
        data,
        col="provider",
        hue="load_zone",
        col_wrap=2,
        aspect=2,
        height=3,
        palette="tab10",
        margin_titles=False,
    )
    g.map(sns.kdeplot, "waiting_ms", fill=True)
    g.set_axis_labels("Waiting Time (ms)", "")

    plt.xlim(0, 600)
    plt.savefig(
        f"geodis-joyplot-coldstarts{includeColdStarts}-outliers{includeOutliers}.png"
    )
    plt.show()


# plot_ecdf(combinedData, False, True)
# GeoDis 1 Excluding outliers
# plot_geodis_data(data, False, True, "bar", 1)
# plot_geodis_data(data, False, True, "box", 1)

# GeoDis 2 Excluding outliers
# plot_geodis_data(data2, False, True, "bar", 2)
# plot_geodis_data(data2, False, True, "box", 2)

# plot_combined_ecdf(combinedData, False, True)
plot_joy(combinedData, False, True)
plot_joy(combinedData, False, False)
plot_joy(combinedData, True, True)
