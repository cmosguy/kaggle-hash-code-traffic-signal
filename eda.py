# %%
import numpy as np
import itertools
import pandas as pd
from copy import deepcopy

from traffic.traffic import Traffic
from datetime import datetime
from tqdm import tqdm

import matplotlib.pyplot as plt


# %%
def make_streets_df(streets, intersections_df, dbg_print=False):
    streets_dict = {}

    start_time = datetime.now()
    i = 0
    for street, values in streets.items():
        streets_dict[i] = {
            'name': street,
            'in_queue': len(values.queue),
            'start_int': values.start_int,
            'end_int': values.end_int,
            'time_used': values.time_used
            # 'green_light': intersections_df[intersections_df.street_in == street]['green_light'].values[0]
            # 'single_street_in': intersections_df[intersections_df.street_in == street]['single_street_in'].values[0],
        }
        i = i + 1

    streets_df = pd.DataFrame.from_dict(streets_dict, "index")
    end_time = datetime.now()
    execution_time = (end_time - start_time).total_seconds() * 1000

    print("Creating streets_df time: {}ms".format(execution_time)) if dbg_print==True else None

    return streets_df


def make_intersections_df(intersections, dbg_print=False):
    intersections_dict = {}

    start_time = datetime.now()
    i = 0
    for index, intersection in intersections.items():
        for street_in_index, street_in in enumerate(intersection.streets_in):
            intersections_dict[i] = {
                'intersection_num': index,
                'street_in': street_in,
                'green_light_time': intersection.green_light_time[street_in_index],
                'single_street_in': True if (len(intersection.streets_in) == 1) else False,
                'green_light': True if (intersection.streets_in[intersection.current_light_index] == street_in) else False
            }
            i = i + 1

    intersections_df = pd.DataFrame.from_dict(intersections_dict, "index")
    end_time = datetime.now()
    execution_time = (end_time - start_time).total_seconds() * 1000

    print("Creating intersections_df time: {}ms".format(execution_time)) if dbg_print==True else False

    return intersections_df


def make_cars_df(cars, streets_df, dbg_print=False):
    start_time = datetime.now()
    cars_dict = {}

    i = 0
    for index, car in cars.items():
        current_street_name = car.path[car.current_street]
        done = True if car.current_street == -1 else False
        cars_dict[i] = {
            'name': car.name,
            'score': car.score,
            'current_street': current_street_name,
            'total_street': car.total_street,
            'done': done,
            'total_travel_time': streets_df.filter(car.path, axis=0)['time_used'].sum()
        }
        i = i + 1

    cars_df = pd.DataFrame.from_dict(cars_dict, "index")
    end_time = datetime.now()
    execution_time = (end_time - start_time).total_seconds() * 1000

    print("Creating cars_df time: {}ms".format(execution_time)) if dbg_print == True else None

    return cars_df


# %%
def myCallback(time, cars, streets, streets_details, intersections):
    global street_queues
    # print('T={}'.format(time))
    intersections_df = make_intersections_df(intersections=intersections, dbg_print=False)

    streets_df = make_streets_df(streets=streets, intersections_df=intersections_df, dbg_print=False).join( intersections_df[['street_in', 'single_street_in', 'green_light']].set_index('street_in'), on='name')
    streets_df.set_index('name', inplace=True)

    cars_df = make_cars_df(cars=cars, streets_df=streets_df, dbg_print=False)

    if(time==0):
        street_queues = streets_df[['in_queue']]
        street_queues.columns = [0]
    else:
        street_queues = pd.concat([street_queues, streets_df[['in_queue']]],axis=1)
        street_queues.columns = list(range(time+1))

    # print(cars_df.head())
    # print(streets_df.head())
    # cars_df.head()


callback = myCallback

# %% we have to restart the simulation with a clean new class to reinitialize
t = Traffic(in_file='./example.in', truncate_cars=False)


t_sl = t.generate_intersection_schedules()
t.generate_submission_file(intersection_schedule_list=t_sl)



#%%

#vector = [2, 1, 2, 1, 1]  # score 1002
# vector = [1, 1, 1, 1, 1]
#t.generate_intersection(vector=vector)
t.read_submission_file()
cars = t.simulate(progress_bar=False, override_end_time=None, _callback=callback)
scheduler_score = t.calculate_simulation_score(cars)
print("Final score: {}".format(scheduler_score))

#%%
cars
# %%

num_streets = len(t.streets)
end_time = 2
street_queues = {}
for street in list(t.streets.keys()):
    street_queues = end_time * [None]
cars = t.simulate(progress_bar=False, override_end_time=end_time, _callback=callback)


# %% debugging with haschcode.in
m = Traffic(in_file='./hashcode.in')
# vector = list(np.random.randint(low=1, high=3, size=len(m.street_detail)))
# m.generate_intersection(vector=vector)
# %%
m_sl = m.generate_intersection_schedules()
m.generate_submission_file(intersection_schedule_list=m_sl,out_file_path='submission.hashcode.txt')
# %%
m.read_submission_file(in_file_path='submission.hashcode.txt')
m_cars = m.simulate(progress_bar=True, _callback=callback)
m_score = m.calculate_simulation_score(m_cars)
print("Final score: {}".format(m_score))


# %%
street_queues.head()
# %%
street_queues.max(axis=1)

# %% first get max values for each time
street_queues.idxmax()

#%%

street_name = 'cbc-cb'


#now plot all the streets in the intersection across time
int_debug = m.street_detail.set_index('name').loc[street_name,'end_int']
streets_in = list(m.street_detail[m.street_detail['end_int'] == int_debug]['name'])
# plt.scatter(street_queues.columns, street_queues.loc[streets_in]) 

def onpick3(event):
    ind = event.ind
    print('onpick3 scatter:')#, ind, np.take(x, ind), np.take(y, ind))
fig = plt.figure()
colnames = street_queues.loc[streets_in].T.columns
ax = street_queues.loc[streets_in].T.plot(y=colnames, figsize = (8,4))
ax.legend(bbox_to_anchor=(1.0, 1.0))
fig.canvas.mpl_connect('pick_event', onpick3)
ax.plot()
# %%
