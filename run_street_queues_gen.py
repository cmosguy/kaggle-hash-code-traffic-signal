
import numpy as np
import pandas as pd

from traffic.traffic import Traffic

import vaex


def set_queues_callback(time, queues):
    global street_queues

    street_queues[time] = queues


in_setup_file='./hashcode.in'
in_submission_file='submission.hashcode.txt'
out_street_queues_hd5_file='street_queues.hashcode.h5'

# in_setup_file='./example.in'
# in_submission_file='submit.example.txt'
# out_street_queues_hd5_file='street_queues.example.h5'


m = Traffic(in_file=in_setup_file)
num_streets = len(m.streets)
callback = set_queues_callback
street_queues = np.zeros((m.end_time, num_streets), dtype=int)
m.read_submission_file(in_file_path=in_submission_file)
m.simulate(progress_bar=True, override_end_time=None, queue_callback=callback)
m_score = m.calculate_simulation_score()
print("Final score: {}".format(m_score))

street_queues_df = vaex.from_pandas(pd.DataFrame(street_queues, columns=list(m.streets.keys())))
street_queues_df.export_hdf5(out_street_queues_hd5_file, progress=True)