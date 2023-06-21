import os
import argparse

from amplpy import AMPL, Environment

from CFLP.GeneticAlgorithm import GeneticAlgorithm
from CFLP.ProblemInstance import ProblemInstance
from CFLP.CFLPSolver import CFLPSolver

from config import AMPL_FILEPATH, DATASET_DIRECTORY, RESULTS_DIRECTORY
from ui import handle_args


args = handle_args(argparse.ArgumentParser())

# initialize AMPL
ampl = AMPL(Environment(AMPL_FILEPATH))
ampl.set_option('presolve', False)

# initialize heuristic algorithm
# Amount of iterations by default = 5
# Note that n_bits has not been configured yet
heuristic = GeneticAlgorithm(n_iter=args.n_iter or 5, n_bits=None)

model_filepath = './ampl_models/cflp_model_relaxed.mod' if args.relaxed else './ampl_models/cflp_model.mod'
solver = CFLPSolver(model_filepath, ampl, heuristic)

problem_instances = []

# load single problem instance
if args.dataset_filepath:
    problem_instances.append(ProblemInstance(args.dataset_filepath))
else:
    # get all datasets inside default dataset directory
    datasets_filepaths = [
        DATASET_DIRECTORY + filepath.name
        for filepath in os.scandir(DATASET_DIRECTORY) if filepath.is_file()
    ]

    # load all problem instances inside default dataset directory
    problem_instances.extend(ProblemInstance(filepath)
                             for filepath in datasets_filepaths)

# solve each problem instance
for problem_instance in problem_instances:
    print(f"[INFO] Solving {problem_instance.dataset_filepath}")

    # setup solver and heuristic algorithm
    solver.problem_instance = problem_instance

    # configure amount of bits for heuristic algorithm
    heuristic.n_bits = problem_instance.n_centers

    # configure mutation rate by calculating mutation rate based on amount of centers
    heuristic.mutation_rate = heuristic.calculate_mutation_rate(
        problem_instance.n_centers)

    # solve and export results to results directory
    results = solver.solve(
        export=True,
        output_filepath=problem_instance.dataset_filepath.replace(
            DATASET_DIRECTORY, RESULTS_DIRECTORY).replace('.txt', '.jpg')
    )
