import pandas as pd
from matplotlib import pyplot as plt

f = pd.read_csv("power.csv", error_bad_lines=False)

#let's convert the voltages to power
print(f["VCC1_VOLTAGE"].max(), f["VCC2_VOLTAGE"].max(), f["VCC3_VOLTAGE"].max())
print(f["VCC1_CURRENT"].max(), f["VCC2_CURRENT"].max(), f["VCC3_CURRENT"].max())
print(f["VCC1_CURRENT"].min(), f["VCC1_CURRENT"].min(), f["VCC1_CURRENT"].min())
#2338 - 550 
f["power"] = f["VCC1_VOLTAGE"] * 796 +  f["VCC2_VOLTAGE"] * 796 + f["VCC3_VOLTAGE"] * 796
f["power"] = f["power"] / 3

#convert the time to a sdatetime object
f["Time"] = pd.to_datetime(f["Time"])
plt.plot_date(f["Time"], f["power"], "k-")
plt.xlabel("Time")
plt.ylabel("Power (mW)")
plt.xticks(rotation=45)
#print the average non-zero power
print("Average power: ", f[f["power"] > 0]["power"].mean())

#now let's load the simulation data
df = pd.read_csv("powerSat.csv")
df["Time"] = pd.to_datetime(df["Time"])
#let's get every 100th point
df = df.iloc[::100]

plt.plot_date(df["Time"], df["Power"], "r-")
plt.tight_layout()
plt.savefig("power.png")