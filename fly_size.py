from overview import *

tables = ["GeoDis", "GeoDis2", "InlineData", "ColdStart", "RampUp"]
pd.set_option("display.max_colwidth", None)


def get_data(table_name):
    conn = sqlite3.connect("20092024.db")
    query = f"SELECT * FROM {table_name}"
    data = pd.read_sql_query(query, conn)
    return data


def query_data(table_name, query):
    conn = sqlite3.connect("experiments.db")
    data = pd.read_sql_query(query, conn)
    return data


def plot_performance_over_time(data):

    g = sns.FacetGrid(data, col="size", col_wrap=4, height=4, aspect=1.5)

    def plot_lines(x, y, **kwargs):
        sns.lineplot(
            x=x,
            y=y,
            marker="o",
            estimator=np.median,
            errorbar=None,
            label="Median",
            **kwargs,
        )
        # Remove 'color' from kwargs if it exists
        kwargs.pop("color", None)
        sns.lineplot(
            x=x,
            y=y,
            marker="x",
            estimator=lambda v: np.percentile(v, 99),
            errorbar=None,
            label="Tail",
            color="red",
            **kwargs,
        )

    g.map(plot_lines, "day", "waiting_ms")
    g.add_legend()
    plt.ylim(0, 8000)
    for ax in g.axes.flat:
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
        ax.set_xlabel("")
        ax.set_ylabel("Latency (ms)")
    plt.savefig("pdf/image_size/fly_imagesize_coldstart_over_time.pdf")
    plt.show()


from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans


def cluster_analysis_for_day(data, day):
    # Filter data for the specified day
    day_data = data[data["day"] == day]

    # Check if there is enough data for clustering
    if day_data.shape[0] < 2:
        print(f"Not enough data for clustering on {day}")
        return

    # Extract relevant features
    features = day_data[["size", "waiting_ms"]]

    # Standardize the features
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(features)

    # Apply K-means clustering
    kmeans = KMeans(n_clusters=2, random_state=42)
    clusters = kmeans.fit_predict(scaled_features)

    # Add cluster labels to the day data
    day_data["cluster"] = clusters

    # Visualize the clusters
    sns.scatterplot(data=day_data, x="size", y="waiting_ms", hue="cluster", marker="o")
    plt.xlabel("Size")
    plt.ylabel("Latency (ms)")
    plt.title(f"Latency vs Size by Cluster for {day}")
    plt.show()


def cluster_analysis_for_all_days(data):
    # Perform clustering for each unique day
    clustered_data = pd.DataFrame()
    for day in data["day"].unique():
        day_data = data[data["day"] == day].copy()
        if day_data.shape[0] < 2:
            continue  # Skip days with insufficient data
        clustered_day_data = cluster_analysis_for_day(day_data, day)
        clustered_data = pd.concat([clustered_data, clustered_day_data])

    # Plot the results in a FacetGrid
    g = sns.FacetGrid(
        clustered_data, col="day", col_wrap=4, height=4, sharex=False, sharey=False
    )
    g.map_dataframe(
        sns.scatterplot, x="size", y="waiting_ms", hue="cluster", marker="o"
    )
    g.add_legend()
    g.set_axis_labels("Size", "Latency (ms)")
    g.set_titles(col_template="{col_name}")
    plt.show()


data = get_data("ColdStartSize")
# Convert the 'start' column to datetime format
data["start"] = pd.to_datetime(data["start"])
# take out size=100 because n=1 for size=100
data = data[data["size"] != 100]
data["day"] = data["start"].dt.date
plot_performance_over_time(data)

# Perform clustering analysis for a specific day
# specific_day = pd.to_datetime("2024-09-05").date()  # Replace with the desired day
# cluster_analysis_for_day(data, specific_day)
# cluster_analysis_for_all_days(data)
