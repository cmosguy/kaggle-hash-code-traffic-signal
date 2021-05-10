from traffic.harmony_search import HarmonySearch
from pyharmonysearch import harmony_search

from multiprocessing import cpu_count
from pprint import pprint

from datetime import datetime

if __name__ == '__main__':
    in_file = './hashcode.in'
    obj_fun = HarmonySearch(in_file=in_file, min_light_time=1, max_light_time=3)
    num_processes = cpu_count()  # use number of logical CPUs
    num_iterations = num_processes * 5  # each process does 5 iterations

    num_processes=1
    num_iterations=1


    results = harmony_search(obj_fun, num_processes=num_processes, num_iterations=num_iterations)
    best_schedule = results.best_harmony

    #override for example.in found 2009 as best result
    # best_schedule = obj_fun.generate_sceduler([3, 1, 3, 3, 2])

    print('Elapsed time: {}\nBest harmony: {}\nBest fitness: {}\nHarmony memories:'.format(results.elapsed_time, results.best_harmony, results.best_fitness))
    obj_fun.traffic.generate_intersection(best_schedule)


    out_file = "./submission.{}.{}_num_proc={}_num_iter={}.csv".format(in_file, datetime.now().strftime("%Y-%m-%d-%H.%M.%S.%f"), num_processes, num_iterations)
    obj_fun.traffic.generate_output_file(outfile=out_file)
    # pprint(results.harmony_memories)
