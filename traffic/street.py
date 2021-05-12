

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
            if cars[car_name].new_street_flag == False:
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
