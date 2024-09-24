import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from overview import *


#  identify the runtime based on the URL
def identify_runtime(row):
    if row["provider"] == "aws":
        if "osyk7zimdu4tctharhnu6j7xdy0jlkkw" in row["url"]:
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


# First, find base median latency for each provider (warm invocation) per each second of the ramp-up test
def find_base_latency_persecond(data):
    data["second"] = pd.to_numeric(data["second"], errors="coerce")
    data["waiting_ms"] = pd.to_numeric(data["waiting_ms"], errors="coerce")
    base_latency = (
        data[data["isCold"] == 0].groupby(["second", "provider"])["waiting_ms"].median()
    )
    return base_latency.reset_index()


def find_base_latency_aggregated(data):
    data["waiting_ms"] = pd.to_numeric(data["waiting_ms"], errors="coerce")
    #  filter out seconds 0 to 2
    data = data[data["second"] > 2]
    base_latency = (
        data[data["isCold"] == 0].groupby(["provider"])["waiting_ms"].median()
    )
    print(base_latency)
    return base_latency.reset_index()


def find_tail_latency_aggregated(data):
    data["waiting_ms"] = pd.to_numeric(data["waiting_ms"], errors="coerce")
    #  filter out seconds 0 to 2
    data = data[data["second"] > 2]
    tail_latency = (
        data[data["isCold"] == 0].groupby(["provider"])["waiting_ms"].quantile(0.99)
    )
    print(tail_latency)
    return tail_latency.reset_index()


def find_cold_latency_aggregated(data, quantile):
    data["waiting_ms"] = pd.to_numeric(data["waiting_ms"], errors="coerce")
    #  only consider cold invocations
    cold_latency = (
        data[data["isCold"] == 1]
        .groupby(["provider", "url"])["waiting_ms"]
        .quantile(quantile)
    )
    print(f"cold latency at {quantile} quantile")
    print(cold_latency.reset_index())
    return cold_latency.reset_index()


def extable():
    # Read query and data
    with open("rampupQuery.sql", "r") as file:
        q = file.read()
        data2 = query_data("RampUp", q)
        base_latency = find_base_latency_persecond(data2)

    # Pivot the DataFrame so that seconds are the columns and providers are the rows
    pivot_table = base_latency.pivot(
        index="provider", columns="second", values="waiting_ms"
    )

    # Export to Excel file
    pivot_table.to_excel("base_latency_table.xlsx")
    # export as a spreadsheet
    find_base_latency_aggregated(data2)
    find_tail_latency_aggregated(data2)


def table_warm_latency(data):
    data["waiting_ms"] = pd.to_numeric(data["waiting_ms"], errors="coerce")
    warm_latency = (
        data[(data["isCold"] == 0)]
        .groupby(["provider", "runtime"])["waiting_ms"]
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
    return warm_latency


def table_latency(data, cold):
    data["waiting_ms"] = pd.to_numeric(data["waiting_ms"], errors="coerce")
    cold_latency = (
        data[(data["isCold"] == cold)]
        .groupby(["provider", "runtime"])["waiting_ms"]
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


# Creates a table with the average median and average tail latency over the first three seconds of the ramp-up test , for each provider and runtime.
# uses the tables/rampup_latency.csv file
def compute_critical_seconds():
    csv_data = pd.read_csv("tables/rampup_latency.csv")

    # filter out seconds > 2
    csv_data = csv_data[csv_data["second"] <= 2]

    grouped = (
        csv_data.groupby(["provider", "runtime"])
        .agg(
            avg_p50=("p50", lambda x: round(np.mean(x), 2)),
            avg_p99=("p99", lambda x: round(np.mean(x), 2)),
        )
        .reset_index()
    )

    return grouped


def get_latest_data(table_name):
    conn = sqlite3.connect("20092024.db")
    query = f"SELECT * FROM {table_name}"
    data = pd.read_sql_query(query, conn)
    return data


pd.set_option("display.max_columns", None)
# colddata = get_data("ColdStart")

# find_cold_latency_aggregated(colddata, 0.5).to_excel("cold_latency_median.xlsx")
# find_cold_latency_aggregated(colddata, 0.99).to_excel("cold_latency_99.xlsx")

warmdata = get_latest_data("WarmStart")

colddata = get_latest_data("ColdStartMem")

# add runtime
colddata["runtime"] = colddata.apply(identify_runtime, axis=1)

# table_latency(colddata, True).to_excel("tables/coldmemory_latency.xlsx")
table_latency(colddata, True).to_csv("tables/coldmemory_latency.csv")

compute_critical_seconds().to_csv("tables/rampup_critical_seconds.csv")
"""
table_warm_latency(warmdata).to_excel("tables/warm_latency_99.xlsx")
table_warm_latency(warmdata).to_csv("tables/warm_latency.csv")
"""
