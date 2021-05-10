from copy import deepcopy

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
        