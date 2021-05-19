from traffic.street import Street
from traffic.intersection import Intersection
from traffic.car import Car
from copy import deepcopy
import csv
import pandas as pd
from tqdm import tqdm
from tqdm import trange
import itertools
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
        self.end_time = self.simulation_config['D']+1
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
        print("Original endtime: {}".format(self.end_time-1))
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
    def calculate_simulation_score(self, cars):
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
    def simulate(self, override_end_time=None, progress_bar=False, _callback=None):
        #     print("Starting traffic simulation.")
        #   Intial cars on streets
        for car in self.cars.values():
            init_street = car.path[0]
            self.streets[init_street].add_queue(car.name, True)
            car.new_street_flag = False
        #   Simulate cars move
        if override_end_time is not None:
            self.end_time = override_end_time+1
            print("Override end time: {}".format(self.end_time-1))
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
                        self.streets[red_street].update_cars_move(self.cars, False)
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
            if _callback:
                _callback(T, deepcopy(self.cars), deepcopy(self.streets), deepcopy(
                    self.street_detail), deepcopy(self.intersections))
        return deepcopy(self.cars)

    def generate_intersection_schedules(self):
        def byGreenSeconds(e):
            return e['green_seconds']
        def byNumberIncomingStreets(s):
            return s['num_incoming_streets']
        intersection_schedule_list = []
        for index, intersection in tqdm(self.intersections.items()):
            intersection_schedule = {
                'order_duration_green_lights': [],
                'id': index,
                'num_incoming_streets': 0
            }
            for street in intersection.streets_in:
                is_start_of_path = 0
                end_street_count = 0
                not_end_street_count = 0
                for c, car in self.cars.items():
                    if car.path[0] == street:
                        is_start_of_path = 1
                    #check if this is the last street and does not require a light schedule
                    if car.path.count(street):
                        if car.path[-1] == street:
                            end_street_count += car.path.index(street) == len(car.path)-1
                        else:
                            not_end_street_count += car.path.index(street) <= len(car.path)
                        
                if (not_end_street_count == 0 and end_street_count > 0):
                    continue
                order_duration_green_light = {
                    'street_name': street,
                    'green_seconds': 1+is_start_of_path
                }
                intersection_schedule['order_duration_green_lights'].append(order_duration_green_light)
            if (len(intersection_schedule['order_duration_green_lights'])):
                intersection_schedule['order_duration_green_lights'].sort(reverse=True, key=byGreenSeconds)
                intersection_schedule_list.append(intersection_schedule)
                intersection_schedule_list.sort(reverse=True, key=byNumberIncomingStreets)
            
            intersection_schedule['num_incoming_streets'] = len(intersection_schedule['order_duration_green_lights'])
                # intersection_percentage = len(intersection_schedule_list) / len(self.intersections)
                # print("{} / {} = {}".format(len(intersection_schedule_list), len(self.intersections), intersection_percentage ))
        return intersection_schedule_list
    def generate_submission_file(self, intersection_schedule_list, out_file_path='submit.example.txt'):
        with open(out_file_path, 'w') as out_file:
            out_file.write("{}\n".format(len(intersection_schedule_list)))
            for intersection_schedule in intersection_schedule_list:
                out_file.write("{}\n{}\n".format(
                    intersection_schedule['id'], intersection_schedule['num_incoming_streets']))
                for order_duration_green_light in intersection_schedule['order_duration_green_lights']:
                    out_file.write("{} {}\n".format(
                        order_duration_green_light['street_name'], order_duration_green_light['green_seconds']))
        print("\nWrote to file: {}".format(out_file_path, end="\n"))

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