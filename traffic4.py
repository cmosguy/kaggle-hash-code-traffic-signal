from traffic.harmony_search import HarmonySearch
from pyharmonysearch import harmony_search

from multiprocessing import cpu_count
from pprint import pprint

from datetime import datetime
import sys, getopt

def main(argv):
    in_file = ''
    num_processes = cpu_count()  # use number of logical CPUs
    num_iterations = 1  # each process does 5 iterations

    try:
        opts, args = getopt.getopt(argv, "hi:pn", ["in_file=", "num_cpus=","num_iterations="])
    except getopt.GetoptError:
        print('traffic.py -i <in_file> -p <num cpus> -n <num_iterations>')
        sys.exit(2)
    
    for opt, arg in opts:
        if opt == '-h':
            print('traffic.py -i <in_file> -p <num cpus> -n <num_iterations>')
            sys.exit()
        elif opt in ("-i", "--in_file"):
            in_file = arg
        elif opt in ("-p", "--num_cpus"):
            num_processes = arg
        elif opt in ("-n", "--num_iterations"):
            num_iterations = arg

    return [in_file, num_processes, num_iterations]



if __name__ == '__main__':

    [in_file, num_processes, num_iterations] = main(sys.argv[1:])


    print('Loading input file: {}'.format(in_file))
    print('Num cpu: {}'.format(num_processes))
    print('Num iterations: {}'.format(num_iterations))

    obj_fun = HarmonySearch(in_file=in_file, min_light_time=1, max_light_time=3)

    results = harmony_search(obj_fun, num_processes=num_processes, num_iterations=num_iterations)
    best_schedule = results.best_harmony

    #override for example.in found 2009 as best result
    # best_schedule = obj_fun.generate_sceduler([3, 1, 3, 3, 2])

    print('Elapsed time: {}\nBest harmony: {}\nBest fitness: {}\nHarmony memories:'.format(results.elapsed_time, results.best_harmony, results.best_fitness))
    obj_fun.traffic.generate_intersection(best_schedule)


    out_file = "./submission.{}_num_proc={}_num_iter={}.csv".format(datetime.now().strftime("%Y-%m-%d-%H.%M.%S.%f"), num_processes, num_iterations)
    obj_fun.traffic.generate_output_file(outfile=out_file)
    print("Wrote submission file: {}".format(out_file))
    # pprint(results.harmony_memories)
