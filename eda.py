# %%
import numpy as np
import itertools
import pandas as pd
from copy import deepcopy

from traffic.traffic import Traffic
from datetime import datetime
from tqdm import tqdm

import matplotlib.pyplot as plt
import vaex


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


# %%
def set_queues_callback(time, queues):
    global street_queues

    street_queues[time] = queues

#%%

callback = set_queues_callback
t = Traffic(in_file='./example.in', truncate_cars=False)

num_streets = len(t.streets)
street_queues = np.zeros((t.end_time, num_streets), dtype=int)
t_sl = t.generate_intersection_schedules()
t.read_submission_file()
t.simulate(progress_bar=False, override_end_time=None, queue_callback=callback)

t_score = t.calculate_simulation_score()
print("Final score: {}".format(t_score))

# %%
street_queues_df = pd.DataFrame(street_queues, columns=list(t.streets.keys()))
street_queues_df.head()

street_name = 'rue-de-moscou'
int_debug = t.street_detail.set_index('name').loc[street_name,'end_int']
streets_in = list(t.street_detail[t.street_detail['end_int'] == int_debug]['name'])

fig = plt.figure()
colnames = street_queues_df.columns
ax = street_queues_df.plot(style='.-', figsize = (8,4))
ax.legend(bbox_to_anchor=(1.0, 1.0))
ax.set_xlabel('Time (T)')
ax.set_ylabel('# of cars in queue')
ax.plot()

# %% debugging with haschcode.in
m = Traffic(in_file='./hashcode.in')
m_sl = m.generate_intersection_schedules()
m.generate_submission_file(intersection_schedule_list=m_sl,out_file_path='submission.hashcode.txt')

# %%
m = Traffic(in_file='./hashcode.in')
num_streets = len(m.streets)
callback = set_queues_callback
street_queues = np.zeros((m.end_time, num_streets), dtype=int)
m.read_submission_file(in_file_path='submission.hashcode.txt')
m.simulate(progress_bar=True, override_end_time=None, queue_callback=callback)
m_score = m.calculate_simulation_score()
print("Final score: {}".format(m_score))


#%%
street_queues_df = pd.DataFrame(street_queues, columns=list(m.streets.keys()))
street_queues_df.to_csv('street_queues.hashcode.csv')

#%%
street_queues_df.head()

#%% top 5 at specific time

fig = plt.figure()

time = 479

top5 = list(street_queues_df.loc[time].T.sort_values(ascending=False)[:5].index)
ax = street_queues_df[top5].plot(style='.-', figsize = (8,4))
ax.legend(bbox_to_anchor=(1.0, 1.0))
ax.set_title("Worst top 5 queues at time={}".format(time))
ax.set_xlabel('Time (T)')
ax.set_ylabel('# of cars in queue')
ax.plot()



# %% first get max values for each time
top10 = list(street_queues_df.max().sort_values(ascending=False)[:10].index)
ax = street_queues_df[top10][2500:4000].plot(style='.-', figsize = (8,4))
ax.legend(bbox_to_anchor=(1.0, 1.0))
ax.set_title("Worst top 10 worst queues")
ax.set_xlabel('Time (T)')
ax.set_ylabel('# of cars in queue')
ax.plot()

#%%
max_queues = street_queues_df.max()
#%%
x_max = street_queues_df.idxmax()
#%%
plt.scatter(x=x_max[:20], y=max_queues[:20])
# ax.legend(bbox_to_anchor=(1.0, 1.0))
# ax.set_title("Worst top 10 worst queues")
# ax.set_xlabel('Time (T)')
# ax.set_ylabel('# of cars in queue')
plt.show()


#%%
#now plot all the streets in the intersection across time
int_debug = m.street_detail.set_index('name').loc[street_name,'end_int']
streets_in = list(m.street_detail[m.street_detail['end_int'] == int_debug]['name'])
# plt.scatter(street_queues.columns, street_queues.loc[streets_in]) 


#%% count the cars starting at time 0
cars_in_street_at_t0 = [car.path[0] for key, car in m.cars.items()]
street_freq_at_t0 = [cars_in_street_at_t0.count(street) for street in cars_in_street_at_t0]
street_freq_at_t0_dict = dict(list(zip(cars_in_street_at_t0, street_freq_at_t0)))

# %%
street_freq_at_t0_dict_sorted = [(street_freq_at_t0_dict[key], key) for key in street_freq_at_t0_dict]
street_freq_at_t0_dict_sorted.sort(reverse=True)

#%%
street_queues_df = vaex.from_pandas(pd.DataFrame(street_queues, columns=list(m.streets.keys())))
# %% convert csv into chunks and storing as hd5 on disk https://vaex.readthedocs.io/en/latest/faq.html#I-have-a-massive-CSV-file-which-I-can-not-fit-all-into-memory-at-one-time.-How-do-I-convert-it-to-HDF5 
street_queues_df = vaex.read_csv('street_queues.hashcode.csv' , convert=True, chunk_size=1_000_000)

# %%

intersection_num = 0 
streets_in_intersection = m.intersections[intersection_num].streets_in
ax = street_queues_df[streets_in_intersection].plot(style='.-', figsize = (8,4))
ax.legend(bbox_to_anchor=(1.0, 1.0))
ax.set_title("Street queeus for intersection {}".format(intersection_num))
ax.set_xlabel('Time (T)')
ax.set_ylabel('# of cars in queue')
ax.plot()
# %%
