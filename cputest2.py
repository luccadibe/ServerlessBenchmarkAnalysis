from overview import *


def plot_cpu_test_data(df):
    # Filter data where status is 200 (successful requests)
    df_success = df[df["status"] == 200]

    # Filter data where status is 503 (unsuccessful requests)
    df_failure = df[df["status"] == 503]

    # Plotting fibDuration for successful requests across different providers and values of n
    plt.figure(figsize=(12, 6))
    sns.boxplot(x="n", y="fibDuration", hue="provider", data=df_success)
    plt.title("Fib Duration by Provider and n (Status == 200)")
    plt.show()

    # Plotting total_ms for both successful and unsuccessful requests across different providers and values of n
    plt.figure(figsize=(12, 6))
    sns.boxplot(x="n", y="total_ms", hue="provider", data=df)
    plt.title("Total Duration by Provider and n (Status 200 and 503)")
    plt.show()

    # Plotting ECDF for fibDuration for successful requests
    g = sns.FacetGrid(df_success, col="provider", hue="n", height=5, aspect=1.5)
    g.map(sns.ecdfplot, "fibDuration")
    g.add_legend()
    g.fig.suptitle("ECDF of fibDuration by Provider and n (Status == 200)", y=1.02)
    plt.show()

    # Plotting total_ms for successful requests across different providers and values of n
    plt.figure(figsize=(12, 6))
    sns.boxplot(x="n", y="total_ms", hue="provider", data=df_success)
    plt.title("Total Duration by Provider and n (Status == 200)")
    plt.show()


def plot_fibDurationVsWaitingTime(df):
    # Filter data where status is 200 (successful requests)
    df_success = df[df["status"] == 200]

    # Plotting waiting_ms against fibDuration for successful requests
    plt.figure(figsize=(12, 6))
    sns.scatterplot(
        x="waiting_ms", y="fibDuration", hue="provider", style="n", data=df_success
    )
    plt.title("Waiting Time vs Fib Duration by Provider (Status == 200)")
    plt.savefig("cputest_waiting_vs_fibduration.png")
    plt.show()


def plot_status(df, includeOutliers=True):
    if not includeOutliers:
        df = remove_outliers(df, "fibDuration", THRESHOLD)

    # Plotting the count of successful and unsuccessful requests
    # plt.figure(figsize=(12, 6))
    g = sns.FacetGrid(df, col="provider", row="n")
    g.map(sns.countplot, "status", hue="n", data=df, color=None)
    # plt.title("Count of Successful and Unsuccessful Requests", y=1.3, fontsize=16)
    plt.legend(title="n")
    plt.savefig(f"cputest_status_lattice_outliers{includeOutliers}.png")
    plt.show()


def plot_fibDuration(df, includeOutliers=True):
    if not includeOutliers:
        df = remove_outliers(df, "fibDuration", THRESHOLD)
    df_success = df[df["status"] == 200]
    # Plotting fibDuration for successful requests across different providers and values of n
    plt.figure(figsize=(12, 6))
    sns.boxplot(x="n", y="fibDuration", hue="provider", data=df_success)
    plt.title("Fib Duration by Provider and n (Status == 200)")
    plt.savefig(f"cputest_fibduration_outliers{includeOutliers}.png")
    plt.show()


def violinplot_fibDuration(df, includeOutliers=True):
    if not includeOutliers:
        df = remove_outliers(df, "fibDuration", THRESHOLD)
    df_success = df[df["status"] == 200]
    # Plotting fibDuration for successful requests across different providers and values of n
    plt.figure(figsize=(12, 6))
    sns.violinplot(x="n", y="fibDuration", hue="provider", data=df_success)
    plt.title("Fib Duration by Provider and n (Status == 200)")
    plt.savefig(f"cputest_fibduration_outliers{includeOutliers}.png")
    plt.show()


def plot_kdepl_n(df, includeOutliers=True, n=25):
    if not includeOutliers:
        df = remove_outliers(df, "fibDuration", THRESHOLD)
    df_success = df[df["status"] == 200]
    df_success = df_success[df_success["n"] == n]
    # for cloudflare, correct fibDuration to be equal to waiting_ms
    df_success.loc[df_success["provider"] == "cloudflare", "fibDuration"] = (
        df_success.loc[df_success["provider"] == "cloudflare", "waiting_ms"] - 19
    )

    # Plotting fibDuration for successful requests across different providers and values of n
    plt.figure(figsize=(12, 6))
    sns.histplot(
        data=df_success, x="fibDuration", hue="provider", fill=True, palette=PALETTE
    )
    # plt.title(f"Fib Duration by Provider and n={n} (Status == 200)")
    if n == 25:
        plt.xlim(0, 35)
    plt.xlabel("Compute Duration (ms)")
    plt.ylabel("Count")
    plt.savefig(f"pdf/cpu/cputest_fibduration_outliers{includeOutliers}_n{n}.pdf")
    plt.show()


def get_quantile_latency(data, provider, n, quantile):
    # Filter for the specific provider and payload size
    filtered_data = data[(data["provider"] == provider)]
    filtered_data = filtered_data[filtered_data["n"] == n]
    if len(filtered_data) == 0:
        return None
    # Compute the quantile latency
    quantile_latency = filtered_data["fibDuration"].quantile(quantile / 100)

    return quantile_latency


def get_std_dev_latency(data, provider, n):
    filtered_data = data[(data["provider"] == provider) & (data["n"] == n)]
    if len(filtered_data) == 0:
        return None
    std_dev = filtered_data["fibDuration"].std()
    return std_dev


# table with median and tail latency (fibDuration) per provider and n
def build_table(data):
    ns = [25, 35, 40, 45]
    providers = data["provider"].unique()
    table = []
    for n in ns:
        for provider in providers:
            filtered_data = data[(data["provider"] == provider) & (data["n"] == n) & (data["status"] == 200)]
            
            if len(filtered_data) == 0:
                continue
            
            median_latency = filtered_data["fibDuration"].median()
            tail_latency = filtered_data["fibDuration"].quantile(0.99)
            std_dev = filtered_data["fibDuration"].std()
            
            if median_latency > 5:
                median_latency = int(median_latency)
            if tail_latency > 5:
                tail_latency = int(tail_latency)
            if std_dev > 5:
                std_dev = int(std_dev)
            
            table.append({
                "provider": provider,
                "n": n,
                "median": median_latency,
                "tail": tail_latency,
                "std_dev": std_dev,
            })
    
    table = pd.DataFrame(table, columns=["provider", "n", "median", "tail", "std_dev"])
    table.to_csv("cputest_latency_table.csv", index=False)
    return table


def plot_fibDuration_per_day_n(data, provider, n):
    data = data[data["provider"] == provider]
    data = data[data["n"] == n]
    data["start"] = pd.to_datetime(data["start"])
    data["day"] = data["start"].dt.day
    data["hour"] = data["start"].dt.hour
    # order should be : from 21 to 31 then from 1 to 6:
    order = list(range(21, 32)) + list(range(1, 7))
    # Plotting fibDuration per day for a specific provider and n
    plt.figure(figsize=(12, 6))
    sns.boxplot(x="day", y="fibDuration", data=data, order=order)
    plt.title(f"Fib Duration per Day for {provider} and n={n}")
    plt.savefig(f"cputest_fibduration_day_{provider}_n{n}.png")
    plt.show()


def plot_fibDuration_per_hour_n(data, provider, n):
    data = data[data["provider"] == provider]
    data = data[data["n"] == n]
    data["start"] = pd.to_datetime(data["start"])
    data["day"] = data["start"].dt.day
    data["hour"] = data["start"].dt.hour
    # Plotting fibDuration per hour for a specific provider and n
    plt.figure(figsize=(12, 6))
    sns.boxplot(x="hour", y="fibDuration", data=data)
    plt.title(f"Fib Duration per Hour for {provider} and n={n}")
    plt.savefig(f"cputest_fibduration_hour_{provider}_n{n}.png")
    plt.show()


def get_status_stats(data, provider, n):
    data = data[data["provider"] == provider]
    data = data[data["n"] == n]
    total = len(data)
    success = len(data[data["status"] == 200])
    failure = len(data[data["status"] == 503])
    unknown = len(data[data["status"] == 0])
    # print(f"Total: {total} | {total/total*100:.2f}%")
    # print(f"Success: {success} | {success/total*100:.2f}%")
    # print(f"Failure: {failure} | {failure/total*100:.2f}%")
    # print(f"Unknown: {unknown} | {unknown/total*100:.2f}%")
    return total, success, failure, unknown


def table_status_stats(data):
    providers = data["provider"].unique()
    ns = [25, 35, 40, 45]
    table = []
    for provider in providers:
        for n in ns:
            total, success, failure, unknown = get_status_stats(data, provider, n)
            table.append(
                {
                    "provider": provider,
                    "n": n,
                    "total": total,
                    "success": success / total * 100,
                    "failure": failure / total * 100,
                    "unknown": unknown / total * 100,
                }
            )
    table = pd.DataFrame(
        table,
        columns=["provider", "n", "total", "success", "failure", "unknown"],
    )
    table.to_csv("tables/cputest_status_table.csv", index=False)
    return table


def plot_cloudflare_fibDuration_vs_watingTime(df):
    df = df[df["provider"] == "cloudflare"]
    df = df[df["status"] == 200]
    df = df[df["n"] == 35]
    plt.figure(figsize=(12, 6))
    sns.scatterplot(x="waiting_ms", y="fibDuration", data=df)
    plt.title("Cloudflare: Waiting Time vs Fib Duration (n=25)")
    plt.savefig("cloudflare_waiting_vs_fibduration.png")
    plt.show()


def plot_median_latency(df):
    df = df[df["status"] == 200]
    ns = [25, 35, 40, 45]

    
    # Plotting median latency for all n values
    sns.lineplot(
        x="n",
        y="fibDuration",
        hue="provider",
        data=df,
        estimator="median",
        palette=PALETTE,
    )
    plt.yscale("log")
    plt.xticks(ns)

    plt.ylabel("Median compute duration (ms)")
    plt.xlabel(" n ")
    plt.savefig("pdf/cpu/cputest_median_latency.pdf")


def plot_kdepl_cloudflare(df, includeOutliers=True, n=25):
    if not includeOutliers:
        df = remove_outliers(df, "fibDuration", THRESHOLD)
    df_success = df[df["status"] == 200]
    df_success = df_success[df_success["provider"] == "cloudflare"]
    df_success = df_success[df_success["n"] == n]
    sns.kdeplot(
        data=df_success, x="waiting_ms", hue="provider", fill=True, palette=PALETTE
    )
    plt.title(f"Fib Duration by Provider and n={n} (Status == 200)")
    plt.xlabel("waiting  (ms)")
    plt.ylabel("Density")
    # plt.savefig(f"cputest_fibduration_outliers{includeOutliers}_n{n}.png")
    plt.show()

def plot_ecdf(data, n):
    plt.figure(figsize=(10, 6))
    
    df_filtered = data[data['n'] == n]
    
    sns.ecdfplot(data=df_filtered, x='fibDuration', hue='provider', palette=PALETTE, legend=True)
    
    plt.xlabel('Duration of compute (ms)')
    plt.ylabel('ECDF')

    plt.grid(True, alpha=0.3)
    
    plt.savefig(f'pdf/cpu/cputest_ecdf_n{n}.pdf')
    plt.close()


def main():
    df = get_data("CpuTest")

    df = df[df["n"] != 38]
    df = df[df["n"] != 15]
    df = df[df["isCold"] == 0]

    # Convert ISO timestamp to pandas datetime
    df['end'] = pd.to_datetime(df['end'], utc=True)

    # Convert Unix timestamp (milliseconds) to pandas datetime
    df['fibStart'] = pd.to_datetime(df['fibStart'], unit='ms', utc=True)

    # Calculate fibDuration for Cloudflare
    df.loc[df["provider"] == "cloudflare", "fibDuration"] = (
        df.loc[df["provider"] == "cloudflare", "end"] - 
        df.loc[df["provider"] == "cloudflare", "fibStart"]
    ).dt.total_seconds() * 1000

    table_status_stats(df)
    build_table(df)
    df = df[df["status"] == 200]
    plot_ecdf(df, 25)
    plot_ecdf(df, 35)
    plot_ecdf(df, 40)
    plot_ecdf(df, 45)


main()
