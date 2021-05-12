from traffic.traffic import Traffic
import numpy as np

m = Traffic(in_file='./hashcode.in')
vector = list(np.random.randint(low=1,high=3, size=len(m.street_detail)))
m.generate_intersection(vector=vector)
m_cars = m.simulate(progress_bar=True)
m_score = m.calculate_simulation_score(m_cars)
print("Final score: {}".format(m_score))