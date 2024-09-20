import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

# Define the RPS pattern
time = list(range(0, 23))  # Total time from 0 to 22 seconds
rps = []

# Ramp up from 1 to 40 in 18 seconds
for t in range(0, 18):
    rps.append(1 + (39 / 17) * t)

# Stay at 40 RPS for 2 seconds
rps.extend([40, 40])

# Scale down to 0 in 2 seconds
rps.extend([40 - (40 / 2) * t for t in range(1, 3)])

# Add the final RPS value to match the length of the time list
rps.append(0)

# Ensure the lengths of time and rps are the same
assert len(time) == len(rps), f"Length mismatch: time={len(time)}, rps={len(rps)}"

# Create a DataFrame
data = pd.DataFrame({"Time (s)": time, "RPS": rps})

# Set the seaborn style
sns.set(style="whitegrid")

# Create the plot
plt.figure(figsize=(10, 6))
sns.lineplot(x="Time (s)", y="RPS", data=data)

# Remove the title
plt.title("")

# Save the plot as a PDF
plt.savefig("rps_plot.pdf", format="pdf")

# Show the plot
plt.show()
