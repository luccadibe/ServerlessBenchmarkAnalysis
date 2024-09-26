import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

tables = ["GeoDis", "GeoDis2", "InlineData", "ColdStart", "RampUp"]
pd.set_option("display.max_colwidth", None)

plt.rcParams["figure.dpi"] = 300
# plt.show = lambda: None  # Disable showing plots


def get_data(table_name):
    conn = sqlite3.connect("26092024.db")
    query = f"SELECT * FROM {table_name}"
    data = pd.read_sql_query(query, conn)
    return data


def query_data(table_name, query):
    conn = sqlite3.connect("26092024.db")
    data = pd.read_sql_query(query, conn)
    return data


PALETTE = {
    "aws": "#dbd642",
    "google": "#374fd4",
    "flyio": "#6f32a8",
    "cloudflare": "orange",
}


def get_headers(table_name):
    conn = sqlite3.connect("experiments.db")
    query = f"PRAGMA table_info({table_name})"
    headers = pd.read_sql_query(query, conn)
    return headers


THRESHOLD = 1.5


def remove_outliers(df, column, threshold=1.5):
    # Calculate Q1 (25th percentile) and Q3 (75th percentile)
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)

    # Calculate the Interquartile Range (IQR)
    IQR = Q3 - Q1

    # Define the upper bound for outliers
    upper_bound = Q3 + threshold * IQR

    # Filter out the outliers
    filtered_df = df[df[column] <= upper_bound]

    return filtered_df


def print_headers():
    for table in tables:
        headers = get_headers(table)
        print(f"Table: {table}")
        print(headers)
        print("\n")
