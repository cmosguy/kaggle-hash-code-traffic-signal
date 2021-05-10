from traffic.traffic import Traffic
import random
import pandas as pd
from copy import deepcopy

MIN_LIGHT_TIME = 1
MAX_LIGHT_TIME = 3


t = Traffic('./example.in')

new_green_light_time = [random.randint(MIN_LIGHT_TIME, MAX_LIGHT_TIME) for _ in range(len(t.street_detail))]
scheduler = pd.DataFrame({'street_name': deepcopy(t.street_detail['name']), 'green_time': new_green_light_time})

print("Calculating score of {} ...".format('scheduler'), end='\t')
t.generate_intersection(scheduler=scheduler)

cars = t.simulate()
scheduler_score = t.calculate_simulation_score(cars)
print("receive {} points".format(scheduler_score), end='\t')