from traffic.street import Street
from traffic.intersection import Intersection
from traffic.car import Car
from copy import deepcopy
import csv
import pandas as pd
from tqdm import tqdm
from tqdm import trange
import itertools
from datetime import datetime

class Traffic():
    simulation_config = []
    streets = {}
    street_detail = []
    cars = {}
    intersections = []
    def __init__(self, in_file='./hashcode.in', truncate_cars=False):
        self.streets = {}
        streets_tmp = {}
        self.street_detail = []
        self.intersections = []
        self.cars = {}
        streets_in_path = set()
        self.total_intersections = None
        self.end_time = 0
        # Open file ready to read
        #f = open(ROOT_DIR + '/hashcode.in', "r")
        f = open(in_file, "r")
        # Read simulation configuration
        simulation_key = ['D', 'I', 'S', 'V', 'F']
        simulation_val = map(int, f.readline().split())
        self.simulation_config = dict(zip(simulation_key, simulation_val))
        self.total_intersections = self.simulation_config['I']
        self.end_time = self.simulation_config['D']
        # Read streets detail
        for _ in range(self.simulation_config['S']):
            type_converted_line = list(
                map(self.convert_type, f.readline().split()))
            self.street_detail.append(type_converted_line)
            new_street = Street(
                type_converted_line[0], type_converted_line[1], type_converted_line[2], type_converted_line[3])
            streets_tmp[type_converted_line[2]] = new_street
        self.street_detail = pd.DataFrame(self.street_detail, columns=[
                                          'start_int', 'end_int', 'name', 'time_used'])
        print("Successfully read {} streets detail".format(
            self.simulation_config['S']))
        # Read cars path
        for i in range(self.simulation_config['V']):
            type_converted_line = list(
                map(self.convert_type, f.readline().split()))
            type_converted_line = [
                type_converted_line[0], type_converted_line[1:]]
            streets_in_path = streets_in_path.union(type_converted_line[1])
            car_name = 'car' + str(i)
            new_car = Car(
                car_name, type_converted_line[0], type_converted_line[1])
            self.cars[car_name] = new_car
        print("Successfully read {} cars paths".format(len(self.cars)))
        # Remove street with no cars
        orig_street_cnt = len(streets_tmp)
        self.street_detail = self.street_detail[self.street_detail['name'].isin(
            streets_in_path)]
        self.streets = {street: streets_tmp[street]
                        for street in streets_in_path}
        self.simulation_config['S'] = len(self.streets)
        self.generate_intersection()
        print("Successfully removed {} streets with no cars".format(
            orig_street_cnt - len(self.streets)))
        print("Total streets: {}".format(len(self.streets)))
        print("Total cars: {}".format(len(self.cars)))
        print("Total intersections: {}".format(self.total_intersections))
        print("Original endtime: {}".format(self.end_time))
        if truncate_cars:
            self.cars = dict(itertools.islice(
                self.cars.items(), truncate_cars))
            print('Truncated cars to total of: {}'.format(len(self.cars.items())))

    # Generate intersections
    def generate_intersection(self):
        intersects = {}
        for i in range(self.total_intersections):
            streets_in = deepcopy(
                list(self.street_detail.loc[self.street_detail['end_int'] == i, 'name']))
            if len(streets_in) > 0:
                green_time = []
                intersects[i] = Intersection(i, streets_in, green_time)
        self.intersections = deepcopy(intersects)
        print("Loaded {} intersections".format(len(self.intersections)), end='\n')

    # Used to calculate simulation score
    def calculate_simulation_score(self):
        total_score = 0
        for car in self.cars.values():
            total_score = total_score + car.score
        return total_score

    # # Change the scheduler of intersections
    # def change_scheduler(intersections, scheduler):
    #     for intersection in intersections.values():
    #         intersection.plug_scheduler(scheduler)
    #     return deepcopy(intersections)
    # Function for type convertion
    def convert_type(self, attr):
        try:
            return int(attr)
        except:
            return attr
    # Return time used in each street
    def get_time_used(self, street_detail, street_name):
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

    def generate_output_file(self, outfile='submission.csv'):
        with open(outfile, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([int(len(self.intersections))])
            for intersection in self.intersections.values():
                writer.writerow([int(intersection.name)])
                writer.writerow([int(len(intersection.streets_in))])
                for street, green_time in zip(intersection.streets_in, intersection.green_light_time):
                    writer.writerow(
                        ["{} {}".format(str(street), int(green_time))])

    def convert_type(self, attr):
        try:
            return int(attr)
        except:
            return attr
    # Function to simulate the traffic flow
    def simulate(self, override_end_time=None, progress_bar=False, callback=None, queue_callback=None):
        #     print("Starting traffic simulation.")
        #   Intial cars on streets
        for car in self.cars.values():
            init_street = car.path[0]
            self.streets[init_street].add_queue(car.name, True)
            car.new_street_flag = False
        #   Simulate cars move
        if override_end_time is not None:
            self.end_time = override_end_time
            print("Override end time: {}".format(self.end_time))
        tprog = range
        if progress_bar:
            tprog = trange

        for T in tprog(self.end_time):
            # for each car reset the new street flag
            for car in self.cars.values():
                car.new_street_flag = False

            for intersection in self.intersections.values():
                if intersection.green_light_time:
                    #   Find streets which currently green and red light
                    green_street, red_streets = intersection.update_light()
                    #   Update cars on street with green signal
                    car_to_new_street = self.streets[green_street].update_cars_move(self.cars, True)
                    #   Update cars on streets with red signal
                    for red_street in red_streets:
                        try:
                            self.streets[red_street].update_cars_move(self.cars, False)
                        except KeyError as e:
                            print("red_street={}".format(red_street))

                    #   Update cars path
                    if (car_to_new_street is not None):
                        # if(self.cars[car_to_new_street].new_street_flag == False):
                        new_street = self.cars[car_to_new_street].update_current_street(
                        )
                        if new_street is not None:
                            self.streets[new_street].add_queue(car_to_new_street, False)
                        else:
                            self.cars[car_to_new_street].update_score(self.simulation_config['F'], self.end_time, T)
        #                     print("{} has reached the destination and received {} points.".format(car_to_new_street, car_score))
                # pbar.update(round(100/((end_time+1)/(T+1))))
            if callback:
                callback(T, deepcopy(self.cars), deepcopy(self.streets), deepcopy(self.street_detail), deepcopy(self.intersections))
            if queue_callback:
                queues = [len(values.queue) for key, values in self.streets.items()]
                queue_callback(T, queues)

    def generate_intersection_schedules(self):
        all_streets = []

        # we only want to collect all the streets in the car paths, except for the last street
        [all_streets.extend(car.path[:-1]) for key, car in self.cars.items()]
        unique_streets = list(set().union(all_streets)) 

        intersections = {}
        for intersection_num in range(self.street_detail['end_int'].max()+1):
            possible_street_names = list(self.street_detail[self.street_detail['end_int'] == intersection_num]['name'])
            street_names = list(set(unique_streets).intersection(possible_street_names))

            intersections[intersection_num] = Intersection(intersection_num, [None] * len(street_names), [1] * len(street_names))

        self.intersections = deepcopy(intersections)

        intersections_df = self.make_intersections_df(intersections=self.intersections)
        streets_df = self.make_streets_df(streets=self.streets, intersections_df=intersections_df).join( intersections_df[['street_in', 'single_street_in', 'green_light']].set_index('street_in'), on='name')
        streets_df.set_index('name', inplace=True)
        cars_df = self.make_cars_df(cars=self.cars, streets_df=streets_df)

        # %% sort cars by lowest travel time and then work your way through
        cars_index_sorted = list(cars_df.sort_values('total_travel_time',ascending=True).index)

        pbar = tqdm(cars_index_sorted)
        for car_index in pbar:
            pbar.set_description("Car processing %s" % car_index)

            T = 0
            #skip last street in car path
            car_path = self.cars["car{}".format(car_index)].path[:-1]
            for index, street in enumerate(car_path):
                #start intersection 
                try:
                    int_num = list(self.street_detail[self.street_detail['name']==street]['end_int'])[0]
                    total_ints = len(self.intersections[int_num].streets_in)

                except KeyError as e:
                    print("key error car{} street={} index={} int_num={}".format(car_index, street, index, int_num))


                #increment T by the street value time used 
                if index > 0:
                    T += streets_df.filter([street], axis=0)['time_used'][0]

                duration_index = T % total_ints

                #check if street all ready defined in tersection schedule, if not set it to new value
                if street in self.intersections[int_num].streets_in:

                    #now, get the duration tick add the remaining timer time on depending where it is 
                    existing_duration_index = self.intersections[int_num].streets_in.index(street)

                    if existing_duration_index < duration_index:
                        #if existing time slot is less than the current duration tick
                        #then you just have to add the time it takes to reach that next tick
                        #you have to wait till it loops back around
                        T += (total_ints - 1 - duration_index) + existing_duration_index + 1
                    else:
                        #if existing time slot is > duration time then subtract total_int - duration_index
                        T += existing_duration_index - duration_index

                else:

                    #if the street has not been defined, but some other street is taking the time slot
                    #then add it to the next available slot time 
                    if self.intersections[int_num].streets_in[duration_index] is None:
                        self.intersections[int_num].streets_in[duration_index] = street
                        # T += duration_index
                    else:
                        #check if there are any available time slots beyond the current time index
                        if None in self.intersections[int_num].streets_in[duration_index:]:
                            remaining_time_duration_index = self.intersections[int_num].streets_in[duration_index:].index(None)
                            new_duration_index = duration_index + remaining_time_duration_index
                            T += remaining_time_duration_index
                            self.intersections[int_num].streets_in[new_duration_index] = street
                        else:
                            #now, if there are no time slots available above the current index then have 
                            # wait and loop around in the timer duration
                            try:
                                looped_time_duration_index = self.intersections[int_num].streets_in[0:duration_index].index(None)
                                T += (total_ints - 1 - duration_index) + looped_time_duration_index + 1
                                self.intersections[int_num].streets_in[looped_time_duration_index] = street
                            except ValueError as e:
                                print("Value error")

                # increment 1 second to pass through intersection
                T += 1  


    def read_submission_file(self, in_file_path='submit.example.txt'):
        in_file = open(in_file_path, 'r')
        lines = in_file.readlines()
        i = 0
        intersection_num = 0
        green_light_flag = False
        intersections = {}
        while i < len(lines):
            if(i == 0):
                total_intersections = int(lines[0].strip())
                i += 1
            elif(i > 0 and green_light_flag == False):
                intersection_num = int(lines[i].strip())
                green_light_flag = True
                i += 1
            else:
                num_streets = int(lines[i].strip())
                i += 1
                street_names = num_streets * [None]
                green_seconds = num_streets * [None]
                for l in range(num_streets):
                    try:
                        street_names[l], green_seconds_str = lines[i + l].strip().split(' ')
                        green_seconds[l] = int(green_seconds_str)
                    except ValueError as e:
                        print("Value error")
                i += num_streets
                green_light_flag = False
                intersections[intersection_num] = Intersection(intersection_num, street_names, green_seconds)

        self.intersections = deepcopy(intersections)

    def make_streets_df(self, streets, intersections_df, dbg_print=False):
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


    def make_intersections_df(self, intersections, dbg_print=False):
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


    def make_cars_df(self, cars, streets_df, dbg_print=False):
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
