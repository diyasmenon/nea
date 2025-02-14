#to do
#check sd calc if its right
#chi sqaured test for gof of model

#last update: added predicting data using rate of change

import time
import math

pm1_vals = [
    12, 13, 13, 14, 14, 15, 16, 17, 18, 18, 19, 20, 21, 21, 22, 23, 24, 25, 26, 27, 
    28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 40, 44, 49, 53, 57, 60, 63, 66, 68, 69, 
    70, 69, 68, 66, 62, 58, 53, 48, 43, 40, 37, 34
]

pm25_vals = [
    32, 33, 33, 34, 34, 35, 36, 37, 38, 39, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 
    49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 60, 64, 69, 74, 80, 84, 88, 92, 95, 97, 
    98, 98, 97, 95, 91, 87, 82, 77, 72, 68, 64, 60
]

pm10_vals = [
    60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79,
    80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 92, 96, 101, 105, 110, 114, 118, 121, 124, 
    126, 127, 128, 128, 127, 125, 122, 118, 114, 110, 106, 102
]

times = list(range(1, 55))

#main--------------------------------------------------------

NUM_LATEST = 10

latest_pm1 = []
latest_pm25 = []
latest_pm10 = []

last_value = 0

pm1_avg = 0
pm25_avg = 0
pm10_avg = 0


#gives the latest x values for each conc of particles
def update_recent_vals(latest_pm1, latest_pm25, latest_pm10, last_value):

    if latest_pm1 == []: #nothing in lists

        #adds first ten values to the list
        for i in range(0, NUM_LATEST):
            latest_pm1.append(pm1_vals[i])
            latest_pm25.append(pm25_vals[i])
            latest_pm10.append(pm10_vals[i])

        last_value = 9

    else:

        #remove first values from each latest list
        latest_pm1.pop(0)
        latest_pm25.pop(0)
        latest_pm10.pop(0)

        #add the "newest value" to the lists
        latest_pm1.append(pm1_vals[last_value + 1])
        latest_pm25.append(pm25_vals[last_value + 1])
        latest_pm10.append(pm10_vals[last_value + 1])

        last_value += 1

    return latest_pm1, latest_pm25, latest_pm10, last_value


def calc_moving_avg_sd(latest_pm1, latest_pm25, latest_pm10):

    #calculate the avg of the latest x data values

    pm1_avg = 0
    pm25_avg = 0
    pm10_avg = 0

    for value in latest_pm1:
        pm1_avg += value

    #print(pm1_avg)
    pm1_avg = pm1_avg/NUM_LATEST

    for value in latest_pm25:
        pm25_avg += value

    pm25_avg = pm25_avg/NUM_LATEST

    for value in latest_pm10:
        pm10_avg += value

    pm10_avg = pm10_avg/NUM_LATEST


    #calculate the avg of the latest x data values

    sum_dists_mean_sq = 0 #sum of the distances to the mean, squared

    for value in latest_pm1:
        sum_dists_mean_sq += (pm1_avg - value) ** 2

    pm1_sd = math.sqrt(sum_dists_mean_sq/NUM_LATEST)

    sum_dists_mean_sq = 0 #sum of the distances to the mean, squared

    for value in latest_pm25:
        sum_dists_mean_sq += (pm25_avg - value) ** 2

    pm25_sd = math.sqrt(sum_dists_mean_sq/NUM_LATEST)

    sum_dists_mean_sq = 0 #sum of the distances to the mean, squared

    for value in latest_pm10:
        sum_dists_mean_sq += (pm10_avg - value) ** 2

    pm10_sd = math.sqrt(sum_dists_mean_sq/NUM_LATEST)


    return pm1_avg, pm25_avg, pm10_avg, pm1_sd, pm25_sd, pm10_sd


def predict_next_val(latest_vals):

    rate_of_change = latest_vals[-1] - latest_vals[-2] #diff in last 2 vals
    next_val = latest_vals[-1] + rate_of_change

    return next_val


#in real one, should run until program ends

for i in range(len(pm1_vals)):

    #print(latest_pm1, latest_pm25, latest_pm10, last_value)

    #gets x latest values
    results = update_recent_vals(latest_pm1, latest_pm25, latest_pm10, last_value)
    latest_pm1 = results[0]
    latest_pm25 = results[1]
    latest_pm10 = results[2] 
    last_value = results[3]

    print(latest_pm1[-1])

    #calc avg and sd of datasets
    results = calc_moving_avg_sd(latest_pm1, latest_pm25, latest_pm10)
    pm1_avg = results[0]
    pm25_avg = results[1]
    pm10_avg = results[2]
    pm1_sd = results[3]
    pm25_sd = results[4]
    pm10_sd = results[5]

    #predict next values
    pm1_next = predict_next_val(latest_pm1)
    pm25_next = predict_next_val(latest_pm25)
    pm10_next = predict_next_val(latest_pm10)

    print('predict: ', pm1_next)

    #print(pm1_avg, pm25_avg, pm10_avg, pm1_sd, pm25_sd, pm10_sd)

    time.sleep(5)

