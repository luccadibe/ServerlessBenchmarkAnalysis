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
    conn = sqlite3.connect("12092024.db")
    query = f"SELECT * FROM {table_name}"
    data = pd.read_sql_query(query, conn)
    return data


def plot_warm_violine(data, subtract_ping=False):
    plt.figure(figsize=(12, 8))
    data["waiting_ms"] = data["waiting_ms"] - data["ping_ms"] * subtract_ping
    sns.boxplot(
        x="runtime",
        hue="provider",
        y="waiting_ms",
        data=data,
        palette=PALETTE,
    )
    plt.title("Warm  Latency by Runtime minus propagation delay")
    plt.xlabel("Runtime")
    plt.ylabel("Latency (ms)")
    plt.ylim(0, 40)
    plt.grid(True)
    plt.legend(title="Provider", loc="upper right")
    # debug : print summary for each provider - runtime
    for provider in data["provider"].unique():
        for runtime in data["runtime"].unique():
            print(
                f"{provider} - {runtime}: {data[(data['provider'] == provider) & (data['runtime'] == runtime)]['waiting_ms'].describe()}"
            )

    plt.savefig(f"warmstarts_boxplot_subtract_ping{subtract_ping}.png")
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

plot_warm_violine(data, True)
