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
	cum_infective = pd.read_csv(os.path.join(dir_name, "num_cumulative_infective.csv"))
	num_infected = pd.read_csv(os.path.join(dir_name, "num_infected.csv"))

	num_steps = math.ceil(cases["Time"].iloc[-1])

	data = pd.merge(symptomatics, hospitalised, on="Time")
	data = pd.merge(data, cum_hospitalised, on="Time")
	data = pd.merge(data, critical, on="Time")
	data = pd.merge(data, deaths, on="Time")
	data = pd.merge(data, cases, on="Time")
	data = pd.merge(data, cum_infective, on="Time")
	data = pd.merge(data, num_infected, on="Time")
	data = data.iloc[::4, :]
	data = data.reset_index(drop=True)
	data["num_cases"] = data["num_cases"].astype(int)
	new_symptomatics = np.zeros((num_steps,)).astype(int)

	#Store whether symptomatics tested as positive and already been hospitalized
	symptomatics = np.zeros((data["num_cases"].iloc[-1], 2), dtype=np.bool_)
	num_tested = np.zeros((num_steps,))
	num_positive = np.zeros((num_steps,))
	
	next_cases = data["num_cases"].iloc[0]
	new_hospitalized = data["num_cumulative_hospitalizations"].iloc[0]

	new_symptomatics[0] = data["num_cases"].iloc[0]
	for j in range(new_symptomatics[0]):
		if np.random.random() < FRAC_TESTED:
			num_tested[0] = num_tested[0] + 1
			
			if np.random.random() < FRAC_POSITIVE:
				num_positive[0] = num_positive[0] + 1
				symptomatics[j, 0] = True

	for j in range(new_hospitalized):
		while True:
			index = np.random.randint(low=0, high=next_cases)
			if not symptomatics[index, 1]:
				symptomatics[index, 1] = True
				if not symptomatics[index, 0]:
					symptomatics[index, 0] = True
					num_tested[i] = num_tested[i] + 1
					num_positive[i] = num_positive[i] + 1

				break

	for i in range(1, num_steps):
		curr_cases = data["num_cases"].iloc[i-1]
		next_cases = data["num_cases"].iloc[i]
		new_symptomatics[i] = data["num_cases"].iloc[i] - data["num_cases"].iloc[i-1]
		new_hospitalized = data["num_cumulative_hospitalizations"].iloc[i] - data["num_cumulative_hospitalizations"].iloc[i-1]

		for j in range(new_symptomatics[i]):
			if np.random.random() < FRAC_TESTED:
				num_tested[i] = num_tested[i] + 1
				
				if np.random.random() < FRAC_POSITIVE:
					num_positive[i] = num_positive[i] + 1
					symptomatics[curr_cases + j, 0] = True

		for j in range(new_hospitalized):
			while True:
				index = np.random.randint(low=0, high=next_cases)
				if not symptomatics[index, 1]:
					symptomatics[index, 1] = True
					if not symptomatics[index, 0]:
						symptomatics[index, 0] = True
						num_tested[i] = num_tested[i] + 1
						num_positive[i] = num_positive[i] + 1

					break



	data["new_symptomatics"] = pd.Series(new_symptomatics).astype(int)
	data["num_tested"] = pd.Series(num_tested).astype(int)
	data["num_positive"] = pd.Series(num_positive).astype(int)

	np.random.seed(SEED)

	"""
	num_tested = np.random.binomial(new_symptomatics, FRAC_TESTED)
	num_positive = np.random.binomial(num_tested, FRAC_POSITIVE)
	data["num_positive_old"] = num_positive
	"""
	data["Day"] = data["Time"].astype("int64")

	data.drop("Time", inplace=True, axis=1)

	data.to_csv(os.path.join(dir_name, "processed_full.csv"), index=False)

	data.drop("num_symptomatic", inplace=True, axis=1)
	data.drop("num_cases", inplace=True, axis=1)

	#Start at first iteration
	index = 0
	for i in range(num_steps):
		if data["num_cumulative_hospitalizations"].iloc[i] != 0:
			index = i
			break

	indexDay = data["Day"].iloc[index]

	data.drop(list(range(0, index)), inplace=True, axis=0)
	data["Day"] = data["Day"] - indexDay + 1


	data = data[["Day", "num_positive", "num_tested", "num_hospitalised", "num_cumulative_hospitalizations", "num_critical", "num_fatalities"]]
	data.to_csv(os.path.join(dir_name, "processed.csv"), index=False)
	data = data[["Day", "num_positive", "num_hospitalised", "num_cumulative_hospitalizations", "num_critical", "num_fatalities"]]
	data.to_csv(os.path.join(dir_name, "processed_no_tested.csv"), index=False)
