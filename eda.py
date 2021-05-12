# %%
import pandas as pd
from copy import deepcopy

from traffic.traffic import Traffic


# %%
def make_streets_df(streets):
    streets_df = pd.DataFrame(
        columns=['name', 'in_queue', 'start_int', 'time_used'])
    for street, values in streets.items():
        streets_df = streets_df.append({'name': street, 'in_queue': len(
            values.queue), 'start_int': values.start_int, 'time_used': values.time_used}, ignore_index=True)

    return streets_df


def make_intersections_df(intersections):
    intersections_df = pd.DataFrame(
        columns=['num', 'street_in', 'green_light_time'])
    for index, intersection in intersections.items():
        for street_in_index, street_in in enumerate(intersection.streets_in):
            intersections_df = intersections_df.append(
                {'num': index, 'street_in': street_in, 'green_light_time': intersection.green_light_time[street_in_index]}, ignore_index=True)
    return intersections_df

def make_cars_df(cars, streets_detail_df):
    cars_df = pd.DataFrame(columns=['name', 'score', 'total_street', 'current_street', 'done'])
    for index, car in cars.items():
        current_street_name = car.path[car.current_street]
        done = True if car.current_street == -1 else False
        cars_df = cars_df.append({'name':car.name, 'score':car.score, 'current_street': current_street_name, 'total_street':car.total_street, 'done':done}, ignore_index=True)
    return cars_df


# %%
def myCallback(time, cars, streets, streets_details):
    print('T={}'.format(time))
    streets_df = make_streets_df(streets=streets)
    cars_df = make_cars_df(cars=cars, streets_detail_df=streets_details)
    print(cars_df.head())
    # print(streets_df.head())
    # cars_df.head()

callback = myCallback

#we have to restart the simulation with a clean new class to reinitialize
t = Traffic(in_file='./example.in')
#vector = [2, 1, 2, 1, 1]  #score 1002
vector = [1, 1, 1, 1, 1]  
t.generate_intersection(vector=vector)
cars = t.simulate(progress_bar=False, override_end_time=None, _callback=callback)
scheduler_score = t.calculate_simulation_score(cars)
print("Final score: {}".format(scheduler_score))


# %%
#debugging with haschcode.in
import pandas as pd
from copy import deepcopy

from traffic.traffic import Traffic
m = Traffic(in_file='./hashcode.in')
# streets_df = make_streets_df(m.streets[:100])
cars_df = make_cars_df(m.cars, m.street_detail)

#%%
type(m.streets)

#%%

import itertools
a = dict(itertools.islice(m.cars.items(),10))

#%%
cars_df = make_cars_df(m.cars, m.street_detail)
cars_df.head()

#%%
m.streets['fifd-bebc'].start_int

#%%
m.street_detail.describe()
# %%
vector = [3, 1, 3, 3, 2]
t.generate_intersection(vector=vector)

intersections_df = make_intersections_df(t.intersections)


intersections_df.head()

#%%
t.street_detail.head()
# %%
