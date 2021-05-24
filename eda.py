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
m.generate_intersection_schedules()
# m.generate_output_file(outfile='submission.hashcode.txt')

#%%
m.generate_output_file(outfile='submission.hashcode.txt')

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
for int_num, intersection in m.intersections.items():
    if 'None' in intersection.streets_in:
        print("int_num={}".format(intersection.name))

#%%
# street_queues_df = pd.DataFrame(street_queues, columns=list(m.streets.keys()))
# street_queues_df.to_csv('street_queues.hashcode.csv')
np.save('street_queues.hashcode.npy', street_queues)

#%%
m = Traffic(in_file='./hashcode.in')
m.read_submission_file(in_file_path='submission.hashcode.txt')
street_queues = np.load('street_queues.hashcode.npy', mmap_mode='r')

#%%
m.intersections[0].streets_in
window = sum(m.intersections[0].green_light_time)

#%% get the strets for intersection 0 from street queues
int_0_queues_indexes = np.where(np.isin(list(m.streets.keys()), m.intersections[0].streets_in))
int_0_queues = np.squeeze(street_queues[:,int_0_queues_indexes],axis=1)

#%%
plt.plot(int_0_queues[:,:10])
plt.show()
#%%
dydx = np.divide(np.diff(int_0_queues[:,:10],axis=0),np.ones((int_0_queues.shape[0]-1,10)))
plt.plot(dydx)
plt.show()

#%%
dydx = np.divide(np.diff(int_0_queues,axis=0),np.ones((int_0_queues.shape[0]-1,int_0_queues.shape[1])))
# plt.plot(dydx)
# plt.show()
#%%
plt.plot(dydx[:,0])
plt.show()

#%%
lst = dydx[:,1]
n=97
chunked = [lst[i:i+n] for i in range(0,len(lst), n)]

for chunk in chunked:
    plt.plot(chunk>0)
plt.show()

#%%
plt.plot(dydx[0:95*3,:] > 0)
plt.show()
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
# %% taking different approach, try to find all unique paths
# conclusion: there are no real unique paths
unique_car_paths = []
unchecked_car_paths = list(m.cars.keys())

unique_car_paths.append(unchecked_car_paths.pop(0))

for unchecked_car_path in unchecked_car_paths:
    unique_found = False
    for unique_car_path in unique_car_paths:
        if set(m.cars[unique_car_path].path) & set(m.cars[unchecked_car_path].path):
            unique_car_paths.remove(unique_car_path) 
            unique_found = False
            break
        else:
            unique_found = True
    
    if unique_found:
        unique_car_paths.append(unchecked_car_path)

