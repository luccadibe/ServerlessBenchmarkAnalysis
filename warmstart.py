from overview import *


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


# Update the palette to include all runtime-provider combinations
palette = {
    "Node.js - aws": "#dbd642",
    "Python - aws": "#dbd642",
    "Node.js - google": "#374fd4",
    "Python - google": "#374fd4",
    "Golang - google": "#374fd4",
    "Node.js - flyio": "#6f32a8",
    "Golang - flyio": "#6f32a8",
    "Node.js - cloudflare": "orange",
    "Python - cloudflare": "orange",
}


def get_warm_data(table_name):
    conn = sqlite3.connect("26092024.db")
    query = f"SELECT * FROM {table_name}"
    data = pd.read_sql_query(query, conn)
    return data


def plot_warm_violine(data, subtract_ping=False):
    data["waiting_ms"] = data["waiting_ms"] - data["ping_ms"] * subtract_ping
    sns.boxplot(
        x="runtime",
        hue="provider",
        y="waiting_ms",
        data=data,
        palette=PALETTE,
    )
    plt.title("")
    plt.xlabel("Runtime")
    plt.ylabel("Latency (ms)")
    plt.ylim(0, 300)
    plt.grid(True)
    plt.legend(title="Provider", loc="upper right")
    # debug : print summary for each provider - runtime
    for provider in data["provider"].unique():
        for runtime in data["runtime"].unique():
            print(
                f"{provider} - {runtime}: {data[(data['provider'] == provider) & (data['runtime'] == runtime)]['waiting_ms'].describe()}"
            )

    plt.savefig(f"pdf/warm_start/warmstarts_boxplot_subtract_ping{subtract_ping}.pdf")
    plt.show()


# something weid happened with flyio between 2020-09-16 and 2020-09-20


def plot_latency_per_day(data):

    g = sns.FacetGrid(
        data, col="provider", row="runtime", margin_titles=True, despine=False
    )

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
    for ax in g.axes.flat:
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
        ax.set_xlabel("days from start of experiment")
        ax.set_ylabel("Latency (ms)")
    g.add_legend()
    plt.savefig("pdf/warm_start/warm_latency_per_day.pdf")
    plt.show()


def plot_hist_provider(data):
    g = sns.FacetGrid(data, col="provider", col_wrap=4, height=4, aspect=1.5)
    g.map(sns.histplot, "waiting_ms", bins=30)
    for ax in g.axes.flat:
        ax.set_xlabel("Latency (ms)")
        ax.set_ylabel("Frequency")
    plt.savefig("pdf/warm_start/warm_hist_provider.pdf")
    plt.show()


def plot_ecdf_warm_facetgrid(data):
    g = sns.FacetGrid(
        data,
        col="runtime",
        hue="provider",
        palette=PALETTE,
        col_wrap=3,
        height=4,
        aspect=1.5,
    )
    g.map(sns.ecdfplot, "waiting_ms")
    g.set_axis_labels("Latency (ms)", "ECDF")
    g.set(xlim=(0, 300))
    g.add_legend()
    plt.savefig("pdf/warm_start/warm_ecdf_facetgrid.pdf")
    plt.show()


def plot_ecdf_warm(data):
    for runtime in data["runtime"].unique():
        print(f"Runtime: {runtime}")
        sns.ecdfplot(
            data=data,
            x="waiting_ms",
            hue="provider",
            palette=PALETTE,
        )
        plt.xlabel("Latency (ms)")
        plt.ylabel("ECDF")
        plt.xlim(0, 300)
        plt.savefig(f"pdf/warm_start/warm_ecdf_{runtime}.pdf")
        plt.show()


"""
Datacenter ping:
google: 32ms
aws: 20.7 ms
flyio : 14.2 ms
cloudflare: 10.8 ms
"""

data = get_warm_data("WarmStart")
data = data[data["isCold"] == 0]

# Convert the 'start' column to datetime format
data["start"] = pd.to_datetime(data["start"])
data["day"] = data["start"].dt.date
print(f"Data shape: {data.shape}")
print("The experiment was run from", data["start"].min(), "to", data["start"].max())

# Add the runtime column
data["runtime"] = data.apply(identify_runtime, axis=1)
# Add the ping column
data["ping_ms"] = data["provider"].map(
    {
        "aws": 20.7,
        "google": 32,
        "flyio": 14.2,
        "cloudflare": 10.8,
    }
)

# plot_warm_violine(data, False)

# only Node.js

plot_ecdf_warm(data[data["runtime"] == "Node.js"])

plot_ecdf_warm(data[data["runtime"] == "Python"])

plot_ecdf_warm(data[data["runtime"] == "Golang"])

# plot_ecdf_warm_facetgrid(data)
# plot_latency_per_day(data)

# plot_hist_provider(data)
