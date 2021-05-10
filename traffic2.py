#%%
import numpy as np
import pandas as pd
from copy import deepcopy
import time
import random
import csv

# Define class of street for keeping properties and methods
class Street:
    def __init__(self, start_int, end_int, name, time_used):
        self.start_int = start_int
        self.end_int = end_int
        self.name = name
        self.time_used = time_used
        self.queue = []
    
    #   Append new car driving on this street     
    def add_queue(self, car_name, isInit):
        if isInit: self.queue.append({car_name: self.time_used})
        else: self.queue.append({car_name: 1})
    
    #   Update cars position on this street     
    def update_cars_move(self, cars, isGreenLight):
        update_car = None
        
        #   Remove car that reached the destination
        if len(self.queue) > 0:
            if cars[list(self.queue[0].keys())[0]].current_street == -1:
                self.queue.pop(0)
        
        #   Update other cars on street         
        for i, car in enumerate(self.queue):
            car_name = list(car.keys())[0]
            car_time_used = list(car.values())[0]
            if isGreenLight:
                if car_time_used >= self.time_used and i == 0:
                    self.queue.remove(car)
                    update_car = car_name
                else:
                    car[car_name] = car[car_name] + 1
            else:
                car[car_name] = car[car_name] + 1 
        return update_car


# Define class of car for keeping properties and methods
class Car:
    def __init__(self, name, total_street, path):
        self.name = name
        self.total_street = total_street
        self.path = path
        self.current_street = 0
        self.score = 0 
    
    #   Calulate score which this car received
    def update_score(self, F, D, T):
        self.score = F + (D - T) if T <= D else 0
        return self.score
    
    #   Update current car position from its path      
    def update_current_street(self):
        if self.current_street >= 0:
            if self.current_street >= self.total_street - 1:
                self.current_street = -1
            else:
                self.current_street = self.current_street + 1
                return self.path[self.current_street]
        return None

# Define class of intersection for keeping properties and methods
class Intersection:
    def __init__(self, name, streets_in, green_light_time):
        self.name = name
        self.streets_in = deepcopy(streets_in)
        self.green_light_time = deepcopy(green_light_time)
        self.current_light_index = 0
        self.timer = 1
        
#     #   Inject new scheduler for the intersection     
#     def plug_scheduler(self, scheduler):
#         self.streets_in = deepcopy(list(scheduler.loc[scheduler['street_name'] == self.name, 'street_name']))
#         self.green_light_time = deepcopy(list(scheduler[scheduler['street_name'].isin(self.streets_in)]['green_time']))
#         self.current_light_index = 0
#         self.timer = 1

    #   Update green light status     
    def update_light(self):

        while self.green_light_time[self.current_light_index] <= 0:
                self.current_light_index = self.current_light_index + 1
                if self.current_light_index > len(self.streets_in)-1:
                    self.current_light_index = 0

        if self.timer > self.green_light_time[self.current_light_index]:
            self.current_light_index = self.current_light_index + 1
            self.timer = 1
        else: self.timer = self.timer + 1
                  
        if self.current_light_index > len(self.streets_in)-1:
            self.current_light_index = 0
            
        return [self.streets_in[self.current_light_index], self.streets_in[:self.current_light_index] + self.streets_in[self.current_light_index+1:]]
        

# Generate intersections
def generate_intersection(simulation_config, street_detail, scheduler):
    intersects = {}
    for i in range(simulation_config['I']):
        streets_in = deepcopy(list(street_detail.loc[street_detail['end_int'] == i, 'name']))
        #   Sort the list respect to scheduler order
        streets_in = deepcopy(list(scheduler[scheduler['street_name'].isin(streets_in)]['street_name']))
        if len(streets_in) > 0:
            green_time = deepcopy(list(scheduler[scheduler['street_name'].isin(streets_in)]['green_time']))
            intersects[i] = Intersection(i, streets_in, green_time)
        
    return deepcopy(intersects)

# Used to calculate simulation score
def calculate_simulation_score(cars):
    total_score = 0
    for car in cars.values():
        total_score = total_score + car.score 
    return total_score

# # Change the scheduler of intersections
# def change_scheduler(intersections, scheduler):
#     for intersection in intersections.values():
#         intersection.plug_scheduler(scheduler)
#     return deepcopy(intersections)

# Function for type convertion
def convert_type(attr):
    try:
        return int(attr)
    except:
        return attr

# Return time used in each street
def get_time_used(street_detail, street_name):
    return street_detail.loc[street_detail['name'] == street_name, 'time_used']

# # Generate output file
# def generate_output_file(intersections):
#     with open('submission.csv', 'w') as file:
#         file.write("{}\n".format(int(len(intersections))))
#         for intersection in intersections.values():
#             file.write("{}\n".format(int(intersection.name)))
#             file.write("{}\n".format(int(len(intersection.streets_in)) ))
#             for street, green_time in zip(intersection.streets_in, intersection.green_light_time):
#                 file.write("{} {}\n".format(str(street), int(green_time)))

# Generate output file
def generate_output_file(intersections):
    with open('submission.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([int(len(intersections))])
        for intersection in intersections.values():
            writer.writerow([int(intersection.name)])
            writer.writerow([int(len(intersection.streets_in))])
            for street, green_time in zip(intersection.streets_in, intersection.green_light_time):
                writer.writerow(["{} {}".format(str(street), int(green_time))])


ROOT_DIR = '.'

streets = {}
streets_tmp = {}
street_detail = []
cars = {}
streets_in_path = set()

# Open file ready to read
#f = open(ROOT_DIR + '/hashcode.in', "r")
f = open(ROOT_DIR + '/example.in', "r")

# Read simulation configuration
simulation_key = ['D', 'I', 'S', 'V', 'F']
simulation_val = map(int, f.readline().split())
simulation_config = dict(zip(simulation_key, simulation_val))

# Read streets detail
for _ in range(simulation_config['S']):
    type_converted_line = list(map(convert_type, f.readline().split()))
    street_detail.append(type_converted_line)
    new_street = Street(type_converted_line[0], type_converted_line[1], type_converted_line[2], type_converted_line[3])
    streets_tmp[type_converted_line[2]] = new_street
street_detail = pd.DataFrame(street_detail, columns= ['start_int', 'end_int', 'name', 'time_used'])

print("Successfully read streets detail")

# Read cars path    
for i in range(simulation_config['V']):
    type_converted_line = list(map(convert_type, f.readline().split()))
    type_converted_line = [type_converted_line[0], type_converted_line[1:]]
    streets_in_path = streets_in_path.union(type_converted_line[1])
    car_name = 'car' + str(i)
    new_car = Car(car_name, type_converted_line[0], type_converted_line[1])
    cars[car_name] = new_car

print("Successfully read cars path")

# Remove street with no cars
street_detail = street_detail[street_detail['name'].isin(streets_in_path)]
streets = {street: streets_tmp[street] for street in streets_in_path}
simulation_config['S'] = len(streets)

print("Successfully remove streets with no cars")

# %%
# Function to simulate the traffic flow
def simulate(streets, cars, intersections, simulation_config):
#     print("Starting traffic simulation.")
    
    #   Intial cars on streets
    for car in cars.values():
        init_street = car.path[0]
        streets[init_street].add_queue(car.name, True)
        
    #   Simulate cars move
    for T in range(simulation_config['D']):
        for intersection in intersections.values():
            
            #   Find streets which currently green and red light             
            green_street, red_streets = intersection.update_light()
            
            #   Update cars on street with green signal
            car_to_new_street = streets[green_street].update_cars_move(cars, True)
            
            #   Update cars on streets with red signal             
            for red_street in red_streets:
                streets[red_street].update_cars_move(cars, False)
                
            #   Update cars path             
            if car_to_new_street is not None:
                new_street = cars[car_to_new_street].update_current_street()
                if new_street is not None:
                    streets[new_street].add_queue(car_to_new_street, False)
                else:
                    car_score = cars[car_to_new_street].update_score(simulation_config['F'], simulation_config['D'], T)
#                     print("{} has reached the destination and received {} points.".format(car_to_new_street, car_score))
    return deepcopy(cars)


#%%
# Function for optimizing the traffic light
def harmony_search(streets, cars, simulate_fn, street_detail, simulation_config):
    
    #   Initialize parameters     
    print("Initializing parameters...", end='\t')
    HMS = 1
    HMCR = 0
    PAR = 0.35
    BW = 0.45
    ITERATION =3 
    SHUFFLE_RATE = 0
    RAND_CHANGE_NUM = 3200
    MIN_LIGHT_TIME = 1
    MAX_LIGHT_TIME = 3
    harmony_memory = pd.DataFrame(columns=['name', 'scheduler', 'score'])
    print("Done")
    
    #   Define simulation function
    print("Initializing objective function...", end='\t')
    obj_fn = simulate_fn
    print("Done")
    
    # Generate initial harmony memories
    print("Generating initial harmonies...")
    for i in range(HMS):
        init_start = time.time()
        tmp_cars = deepcopy(cars)
        tmp_streets = deepcopy(streets)
        #   Randomly generate scheduler
        new_green_light_time = [random.randint(MIN_LIGHT_TIME, MAX_LIGHT_TIME) for _ in range(len(street_detail))]
        scheduler = pd.DataFrame({'street_name': deepcopy(street_detail['name']), 'green_time': new_green_light_time})
        
        print("Calculating score of {} ...".format('scheduler' + str(i)), end='\t')
        #   Simulate and calculate simulation's score  
        intersections = generate_intersection(simulation_config, street_detail, scheduler)
        tmp_cars = obj_fn(tmp_streets, tmp_cars, intersections, simulation_config)
        scheduler_score = calculate_simulation_score(tmp_cars)
        print("receive {} points".format(scheduler_score), end='\t')
        
        #   Append new scheduler to memory
        harmony_memory = harmony_memory.append({'name': 'scheduler' + str(i), 'scheduler': scheduler, 'score': scheduler_score}, ignore_index=True)
        init_stop = time.time()
        print('Total time used: {} mins'.format((init_stop-init_start)/60))
    
    print("Done")

    #   Start optimizing     
    print("Optimizing...")
    for i in range(ITERATION):
        optimize_start = time.time()
        print("Start iteration {}".format(str(i)), end='\t')
        tmp_cars = deepcopy(cars)
        tmp_streets = deepcopy(streets)
        
        #   Randomly select a harmony in memory
        selected_index = random.randint(0,HMS-1)
        new_harmony = deepcopy(harmony_memory.loc[selected_index])
                
        #   Randomly select one from memory
        if random.random() > HMCR:    
            
            #   Select wheather to shuffle or not             
            if random.random() > SHUFFLE_RATE:
                print('NEW HARMONY', new_harmony)
                new_harmony['scheduler'] = new_harmony['scheduler'].sample(frac=1)
                
            new_harmony_green_light_time = deepcopy(list(new_harmony['scheduler']['green_time']))
            for _ in range(RAND_CHANGE_NUM):
                random_adjusted_pitch = random.randint(0, len(new_harmony_green_light_time)-1)             
                #   if light interval > 1                 
                if new_harmony_green_light_time[random_adjusted_pitch] > 1:
                    new_harmony_green_light_time[random_adjusted_pitch] = new_harmony_green_light_time[random_adjusted_pitch] - BW * (2 * random.random())
            
            #   Adjust pitch
            if random.random() > PAR:
                for _ in range(RAND_CHANGE_NUM):
                    random_adjusted_pitch = random.randint(0, len(new_harmony_green_light_time)-1)
                    new_harmony_green_light_time[random_adjusted_pitch] = new_harmony_green_light_time[random_adjusted_pitch] + BW * (3 * random.random())
                
        #   Generate new harmony by random
        else:
            lower_bound = min(new_harmony['scheduler']['green_time'])
            upper_bound = max(new_harmony['scheduler']['green_time'])
            new_harmony_green_light_time = lower_bound + (upper_bound - lower_bound) * np.array([random.randint(MIN_LIGHT_TIME, MAX_LIGHT_TIME) for _ in range(len(new_harmony_green_light_time))])
        
        new_scheduler = pd.DataFrame({'street_name': deepcopy(new_harmony['scheduler']['street_name']), 'green_time': deepcopy(list(new_harmony_green_light_time))})
            
        #   Simulate and calculate new harmony score
        new_intersections = generate_intersection(simulation_config, street_detail, new_scheduler)
        tmp_cars = obj_fn(tmp_streets, tmp_cars, new_intersections, simulation_config)
        new_harmony_score = calculate_simulation_score(tmp_cars)
        
        #   Update memory
        if harmony_memory.loc[np.argmin(harmony_memory['score']), 'score'] < new_harmony_score:
            harmony_memory.loc[np.argmin(harmony_memory['score']), 'scheduler'] = deepcopy([new_scheduler])
            harmony_memory.loc[np.argmin(harmony_memory['score']), 'score'] = new_harmony_score
        
        #print('HARMONY_MEMORY: ', harmony_memory[0, 'scheduler'])
        
        print('Best memory score: {}'.format(harmony_memory.loc[np.argmax(harmony_memory['score']), 'score']), end='\t')
        print('Worst memory score: {}'.format(harmony_memory.loc[np.argmin(harmony_memory['score']), 'score']), end='\t')
            
        optimize_stop = time.time()
        print('Total time used: {} mins'.format((optimize_stop-optimize_start)/60))
        
    print("Optimizatin is done!")

    return deepcopy(harmony_memory)
# %%
# Optimize the solution
start = time.time()
memory = harmony_search(streets, cars, simulate, street_detail, simulation_config)
stop = time.time()
print("Simulating time: {} mins".format((stop-start)//60))
# %%
# Generate output
best_memory = deepcopy(memory.loc[np.argmax(memory['score'])])
mem_scheduler = best_memory['scheduler']
best_intersections = generate_intersection(simulation_config, street_detail, mem_scheduler)
generate_output_file(best_intersections)
# %%
