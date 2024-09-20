import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from overview import *


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


def table_warm_latency(data, quantile):
    data["waiting_ms"] = pd.to_numeric(data["waiting_ms"], errors="coerce")
    warm_latency = (
        data[(data["isCold"] == 0)]
        .groupby(["provider", "url"])["waiting_ms"]
        .agg(
            [
                ("count", "count"),
                ("mean", "mean"),
                ("std", "std"),
                ("min", "min"),
                ("p50", lambda x: np.percentile(x, 50)),
                ("p99", lambda x: np.percentile(x, 99)),
                ("max", "max"),
            ]
        )
        .reset_index()
    )
    return warm_latency


def get_latest_data(table_name):
    conn = sqlite3.connect("12092024.db")
    query = f"SELECT * FROM {table_name}"
    data = pd.read_sql_query(query, conn)
    return data


pd.set_option("display.max_columns", None)
# colddata = get_data("ColdStart")

# find_cold_latency_aggregated(colddata, 0.5).to_excel("cold_latency_median.xlsx")
# find_cold_latency_aggregated(colddata, 0.99).to_excel("cold_latency_99.xlsx")

warmdata = get_latest_data("WarmStart")

table_warm_latency(warmdata, 0.99).to_excel("warm_latency_99.xlsx")
