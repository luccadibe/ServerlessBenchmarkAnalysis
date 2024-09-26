from overview import *

tables = ["GeoDis", "GeoDis2", "InlineData", "ColdStart", "RampUp"]
pd.set_option("display.max_colwidth", None)


def get_data(table_name):
    conn = sqlite3.connect("26092024.db")
    query = f"SELECT * FROM {table_name}"
    data = pd.read_sql_query(query, conn)
    return data


def query_data(table_name, query):
    conn = sqlite3.connect("experiments.db")
    data = pd.read_sql_query(query, conn)
    return data


def plot_performance_over_time(data, simplify=False):
    # simplify: only sizes 200 , 400 ,800 ,2000
    if simplify:
        data = data[data["size"].isin([200, 400, 800, 2000])]
    # Adjust the size by adding 353 MB to each entry
    data["size"] = data["size"].apply(lambda x: x + 353)

    g = sns.FacetGrid(data, col="size", col_wrap=2, height=2, aspect=1.5)

    def plot_lines(x, y, **kwargs):
        sns.lineplot(
            x=x,
            y=y,
            marker=None,
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
            marker=None,
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
        ax.set_xlabel("days from start of experiment")
        ax.set_ylabel("Latency (ms)")
    plt.savefig(
        f"pdf/image_size/fly_imagesize_coldstart_over_time_simple{simplify}.pdf"
    )
    plt.show()


def plot_boxplot_size(data):
    # Adjust the size by adding 353 MB to each entry
    data["size"] = data["size"].apply(lambda x: x + 353)
    sns.boxplot(
        data=data, x="size", y="waiting_ms", flierprops={"marker": "x"}, fliersize=1
    )
    plt.xlabel("Image Size in MB")
    plt.ylabel("Latency (ms)")
    # plt.title("Latency Distribution by Image Size")
    plt.ylim(0, 8000)
    plt.savefig("pdf/image_size/fly_imagesize_boxplot.pdf")
    plt.show()


data = get_data("ColdStartSize")
# Convert the 'start' column to datetime format
data["start"] = pd.to_datetime(data["start"])
# take out size=100 because n=1 for size=100
data = data[data["size"] != 100]
data["day"] = data["start"].dt.date


# debug
print(data["size"].unique())

plot_performance_over_time(data, simplify=True)

plot_boxplot_size(data)
