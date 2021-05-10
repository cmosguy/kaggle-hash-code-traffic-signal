from traffic.street import Street
from traffic.intersection import Intersection
from traffic.car import Car
from copy import deepcopy

import csv
import pandas as pd


class Traffic():

    simulation_config = []
    streets = {}
    street_detail = []
    cars = {}
    intersections = []

    def __init__(self, in_file='./hashcode.in'):

        self.streets = {}
        streets_tmp = {}
        self.street_detail = []
        self.intersections = []
        self.cars = {}
        streets_in_path = set()

        # Open file ready to read
        #f = open(ROOT_DIR + '/hashcode.in', "r")
        f = open(in_file, "r")

        # Read simulation configuration
        simulation_key = ['D', 'I', 'S', 'V', 'F']
        simulation_val = map(int, f.readline().split())
        self.simulation_config = dict(zip(simulation_key, simulation_val))

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

        print("Successfully read streets detail")

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

        print("Successfully read cars path")

        # Remove street with no cars
        self.street_detail = self.street_detail[self.street_detail['name'].isin(streets_in_path)]
        self.streets = {street: streets_tmp[street] for street in streets_in_path}
        self.simulation_config['S'] = len(self.streets)

        print("Successfully remove streets with no cars")

    # Generate intersections
    def generate_intersection(self, scheduler):
        intersects = {}
        for i in range(self.simulation_config['I']):
            streets_in = deepcopy(
                list(self.street_detail.loc[self.street_detail['end_int'] == i, 'name']))
            #   Sort the list respect to scheduler order
            streets_in = deepcopy(
                list(scheduler[scheduler['street_name'].isin(streets_in)]['street_name']))
            if len(streets_in) > 0:
                green_time = deepcopy(
                    list(scheduler[scheduler['street_name'].isin(streets_in)]['green_time']))
                intersects[i] = Intersection(i, streets_in, green_time)

        self.intersections = deepcopy(intersects)
        #print("Loaded {} intersections".format(len(self.intersections)), end='\n')

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

    def simulate(self):
        #     print("Starting traffic simulation.")

        #   Intial cars on streets
        for car in self.cars.values():
            init_street = car.path[0]
            self.streets[init_street].add_queue(car.name, True)

        #   Simulate cars move
        for T in range(self.simulation_config['D']):
            for intersection in self.intersections.values():

                #   Find streets which currently green and red light
                green_street, red_streets = intersection.update_light()

                #   Update cars on street with green signal
                car_to_new_street = self.streets[green_street].update_cars_move(
                    self.cars, True)

                #   Update cars on streets with red signal
                for red_street in red_streets:
                    self.streets[red_street].update_cars_move(self.cars, False)

                #   Update cars path
                if car_to_new_street is not None:
                    new_street = self.cars[car_to_new_street].update_current_street()
                    if new_street is not None:
                        self.streets[new_street].add_queue(car_to_new_street, False)
                    else:
                        car_score = self.cars[car_to_new_street].update_score(
                            self.simulation_config['F'], self.simulation_config['D'], T)
    #                     print("{} has reached the destination and received {} points.".format(car_to_new_street, car_score))
        return deepcopy(self.cars)
