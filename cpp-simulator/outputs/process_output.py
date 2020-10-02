import argparse
import os
import pandas as pd
import numpy as np
import math

if __name__ == "__main__":
	FRAC_TESTED = 0.75
	FRAC_POSITIVE = 0.8
	SEED = 11

	parser = argparse.ArgumentParser(description='')
	parser.add_argument("-dir", default=None, type=str)

	args = parser.parse_args()

	dir_name = args.dir

	symptomatics = pd.read_csv(os.path.join(dir_name, "num_symptomatic.csv"))
	hospitalised = pd.read_csv(os.path.join(dir_name, "num_hospitalised.csv"))
	cum_hospitalised = pd.read_csv(os.path.join(dir_name, "num_cumulative_hospitalizations.csv"))
	critical = pd.read_csv(os.path.join(dir_name, "num_critical.csv"))
	deaths = pd.read_csv(os.path.join(dir_name, "num_fatalities.csv"))
	cases = pd.read_csv(os.path.join(dir_name, "num_cases.csv"))

	num_steps = math.ceil(cases["Time"].iloc[-1])

	data = pd.merge(symptomatics, hospitalised, on="Time")
	data = pd.merge(data, cum_hospitalised, on="Time")
	data = pd.merge(data, critical, on="Time")
	data = pd.merge(data, deaths, on="Time")
	data = pd.merge(data, cases, on="Time")
	data = data.iloc[::4, :]
	new_symptomatics = np.zeros((num_steps,))

	for i in range(num_steps -1, 0, -1):
		new_symptomatics[i] = data["num_cases"].iloc[i] - data["num_cases"].iloc[i-1]
	new_symptomatics[0] = data["num_cases"].iloc[0]

	new_symptomatics = new_symptomatics.astype(int)

	data["new_symptomatics"] = pd.Series(new_symptomatics)
	print(new_symptomatics)

	np.random.seed(SEED)
	num_tested = np.random.binomial(new_symptomatics, FRAC_TESTED)
	num_positive = np.random.binomial(num_tested, FRAC_POSITIVE)
	data["num_positive"] = num_positive
	data["Day"] = data["Time"].astype("int64")
	data.drop("Time", inplace=True, axis=1)
	data.drop("num_symptomatic", inplace=True, axis=1)
	data.drop("num_cases", inplace=True, axis=1)

	#Start at first iteration
	index = 0
	for i in range(num_steps):
		if data["num_cumulative_hospitalizations"].iloc[i] != 0:
			index = i
			break

	print(data)
	indexDay = data["Day"].iloc[index]
	print(index)

	data.drop(list(range(0, index*4, 4)), inplace=True, axis=0)
	data["Day"] = data["Day"] - indexDay + 1


	data = data[["Day", "num_positive", "num_hospitalised", "num_cumulative_hospitalizations", "num_critical", "num_fatalities"]]
	data.to_csv(os.path.join(dir_name, "processed.csv"), index=False)
