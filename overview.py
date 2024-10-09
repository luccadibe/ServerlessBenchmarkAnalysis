import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import csv
from datetime import datetime, timedelta
import os
from dateutil import parser

tables = ["GeoDis", "GeoDis2", "InlineData", "ColdStart", "RampUp"]
pd.set_option("display.max_colwidth", None)

plt.rcParams["figure.dpi"] = 300
#plt.show = lambda: None  # Disable showing plots


def get_data(table_name):
    conn = sqlite3.connect("experiments.db")
    query = f"SELECT * FROM {table_name}"
    data = pd.read_sql_query(query, conn)
    return data


def query_data(table_name, query):
    conn = sqlite3.connect("experiments.db")
    data = pd.read_sql_query(query, conn)
    return data


PALETTE = {
    "aws": "#dbd642",
    "google": "#374fd4",
    "flyio": "#6f32a8",
    "cloudflare": "orange",
}

FLYER_PROPS = {
    "marker": "x",
    "markersize": 1,
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


def output_experiment_schedule():
    conn = sqlite3.connect("experiments.db")
    experiment_data = []

    # Define the experiments and their corresponding tables
    experiments = [
        ("GeoDis", ["GeoDis", "GeoDis2"]),
        ("ColdStart", ["ColdStart"]),
        #("InlineData", ["InlineData"]),
        ("RampUp", ["RampUp"]),
        ("ColdStartMem", ["ColdStartMem"]),
        ("ColdStartSize", ["ColdStartSize"]),
        ("CpuTest", ["CpuTest"]),
        ("WarmStart", ["WarmStart"])
    ]

    for experiment_name, table_names in experiments:
        start_dates = []
        end_dates = []

        for table_name in table_names:
            query = f"SELECT MIN(start) as start_date, MAX(end) as end_date FROM {table_name}"
            result = pd.read_sql_query(query, conn)
            
            if not result.empty and not result['start_date'].isnull().all() and not result['end_date'].isnull().all():
                start_dates.append(result['start_date'].iloc[0])
                end_dates.append(result['end_date'].iloc[0])

        if start_dates and end_dates:
            start_date = min(start_dates)
            end_date = max(end_dates)
            
            start_datetime = parser.parse(start_date)
            end_datetime = parser.parse(end_date)
            
            duration = (end_datetime - start_datetime).days + 1  # Adding 1 to include both start and end days
            
            experiment_data.append({
                "Experiment": experiment_name,
                "Start Date": start_datetime.strftime("%d-%m-%Y"),
                "End Date": end_datetime.strftime("%d-%m-%Y"),
                "Duration (days)": duration
            })

    # Sort experiments by start date
    experiment_data.sort(key=lambda x: datetime.strptime(x["Start Date"], "%d-%m-%Y"))

    # Write to CSV file
    output_file = "./tables/experiment_schedule.csv"
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, "w", newline="") as csvfile:
        fieldnames = ["Experiment", "Start Date", "End Date", "Duration (days)"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for row in experiment_data:
            writer.writerow(row)

    print(f"Experiment schedule has been written to {output_file}")

# Call the function to generate the CSV file
#output_experiment_schedule()
