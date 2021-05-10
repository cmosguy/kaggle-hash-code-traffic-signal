from pyharmonysearch import ObjectiveFunctionInterface
import random
from bisect import bisect_left

from traffic.traffic import Traffic
from copy import deepcopy

import pandas as pd

class HarmonySearch(ObjectiveFunctionInterface):

    """
        This is a toy objective function that contains a mixture of continuous and discrete variables.

        Goal:

            maximize -(x^2 + (y+1)^2) + 4
            The maximum is 4 at (0, -1).

        In this implementation, x is a discrete variable with choices ranging from -100 to 100 in increments of 1.
        y is still a continuous variable.

        Warning: Stochastically solving a linear system is dumb. This is just a toy example.
    """

    def __init__(self, min_light_time = 1, max_light_time=3, in_file='./example.in'):
        self.traffic = Traffic(in_file=in_file)
        self.scheduler = []

        num_streets = len(self.traffic.streets)

        self._lower_bounds = num_streets * [None]
        self._upper_bounds = num_streets * [None]
        self._variable = num_streets * [True]


        self._discrete_values = num_streets * [[x for x in range(min_light_time, max_light_time+1)]]

        # define all input parameters
        self._maximize = True  # do we maximize or minimize?
        self._max_imp = 50000  # maximum number of improvisations
        self._hms = 100  # harmony memory size
        self._hmcr = 0.75  # harmony memory considering rate
        self._par = 0.5  # pitch adjusting rate
        self._mpap = 0.25  # maximum pitch adjustment proportion (new parameter defined in pitch_adjustment()) - used for continuous variables only
        self._mpai = 10  # maximum pitch adjustment index (also defined in pitch_adjustment()) - used for discrete variables only

    def generate_sceduler(self, vector):
        self.scheduler = pd.DataFrame({'street_name': deepcopy(self.traffic.street_detail['name']), 'green_time': vector})
        return self.scheduler


    def get_fitness(self, vector):

        self.generate_sceduler(vector)

        self.traffic.generate_intersection(scheduler=self.scheduler)
        cars = self.traffic.simulate()
        scheduler_score = self.traffic.calculate_simulation_score(cars)

        return scheduler_score

    def get_value(self, i, j=None):
        if self.is_discrete(i):
            if j:
                return self._discrete_values[i][j]
            return self._discrete_values[i][random.randint(0, len(self._discrete_values[i]) - 1)]
        return random.uniform(self._lower_bounds[i], self._upper_bounds[i])

    def get_lower_bound(self, i):
        """
            This won't be called except for continuous variables, so we don't need to worry about returning None.
        """
        return self._lower_bounds[i]

    def get_upper_bound(self, i):
        """
            This won't be called except for continuous variables.
        """
        return self._upper_bounds[i]

    def get_num_discrete_values(self, i):
        if self.is_discrete(i):
            return len(self._discrete_values[i])
        return float('+inf')

    def get_index(self, i, v):
        """
            Because self.discrete_values is in sorted order, we can use binary search.
        """
        return HarmonySearch.binary_search(self._discrete_values[i], v)

    @staticmethod
    def binary_search(a, x):
        """
            Code courtesy Python bisect module: http://docs.python.org/2/library/bisect.html#searching-sorted-lists
        """
        i = bisect_left(a, x)
        if i != len(a) and a[i] == x:
            return i
        raise ValueError

    def is_variable(self, i):
        return self._variable[i]

    def is_discrete(self, i):
        return self._discrete_values[i] is not None

    def get_num_parameters(self):
        return len(self._lower_bounds)

    def use_random_seed(self):
        return hasattr(self, '_random_seed') and self._random_seed

    def get_max_imp(self):
        return self._max_imp

    def get_hmcr(self):
        return self._hmcr

    def get_par(self):
        return self._par

    def get_hms(self):
        return self._hms

    def get_mpai(self):
        return self._mpai

    def get_mpap(self):
        return self._mpap

    def maximize(self):
        return self._maximize
