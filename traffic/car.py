
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
