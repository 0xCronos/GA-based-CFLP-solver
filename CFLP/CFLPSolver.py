import time

import traceback

from amplpy import AMPL
import matplotlib.pyplot as plt

from CFLP.GeneticAlgorithm import GeneticAlgorithm
from CFLP.ProblemInstance import ProblemInstance


class CFLPSolver:
    def __init__(self, model_filepath, ampl: AMPL, heuristic: GeneticAlgorithm, problem_instance: ProblemInstance = None):
        self.model_filepath = model_filepath

        self.ampl = ampl
        self.heuristic = heuristic
        self.problem_instance = problem_instance

    def solve(self, export=False, output_filepath=False):
        self.ampl.reset()

        self.__read_model()
        self.__read_data()

        try:
            start_time = time.time()

            best_x, best_score, found_solutions, best_solutions_by_generation = self.heuristic.run(
                ampl=self.ampl)

            execution_time = time.time() - start_time

            results = [best_x, best_score, found_solutions,
                       best_solutions_by_generation, execution_time]

            if export and output_filepath:
                self.__export_results_as_jpg(results, output_filepath)

            self.summary(results)

            return results

        except Exception as e:
            print(f'[ERROR] error while executing heuristic: {e}')
            traceback.print_exc()

    def summary(self, results):
        best_x, best_score, _, _, execution_time = results
        print(
            f'\n[RESULTS]\n\n{best_x=}\n{best_score=}\n{execution_time=} seconds\n')

    def __export_results_as_jpg(self, results, output_filepath):
        _, best_score, found_solutions, best_solutions_by_generation, execution_time = results

        if best_solutions_by_generation and found_solutions:
            figure, (ax1, ax2) = plt.subplots(2, 1)
            figure.set_figwidth(10)
            figure.set_figheight(10)

            ax1.set_title('Convergencia algoritmo genético')

            # print summary inside subplot
            summary = f'Mejor costo: {round(best_score, 4)}\n\nTiempo de ejecución: {round(execution_time, 4)}'
            summary += f'segundos\n\nIndividuos probados: {len(found_solutions)}'
            summary += f'\n\nIteraciones: {self.heuristic.n_iter}'

            ax1.text(0.55, 0.65, summary, horizontalalignment='left',
                     verticalalignment='center', transform=ax1.transAxes, color='green')

            ax1.set(xlabel='Generaciones', ylabel='Costos')
            ax1.plot([sol[1] for sol in best_solutions_by_generation])
            offset = len(best_solutions_by_generation) // 2

            plt.xticks(range(1, len(best_solutions_by_generation), 2))

            ax2.plot([sol[1] for sol in found_solutions])
            ax2.set(xlabel='Soluciones encontradas', ylabel='Costos')
            offset = round(len(found_solutions) //
                           (len(found_solutions) // round(self.heuristic.n_iter * 5)))
            plt.xticks(range(1, len(found_solutions), offset))

            plt.savefig(output_filepath)
            plt.close()
        else:
            figure, (ax1) = plt.subplots(1)

            summary = f'No se encontraron soluciones\n\nTiempo de ejecución: {round(execution_time, 4)} segundos\n\nIteraciones realizadas: {self.heuristic.n_iter}'
            ax1.text(0.5, 0.5, summary, horizontalalignment='center',
                     verticalalignment='center', transform=ax1.transAxes, color='red')

            plt.savefig(output_filepath)
            plt.close()

    def __read_model(self):
        self.ampl.read(filename=self.model_filepath)

    def __read_data(self):
        """ load .dat file saved by problem_instance
        """
        # create filepath for saving data
        problem_instance_filepath = self.problem_instance.dataset_filepath.replace(
            'datasets', 'data').replace('txt', 'dat')

        # save .dat file with the problem instance values
        self.problem_instance.save(problem_instance_filepath)

        # interprets AMPL data file (.dat)
        self.ampl.read_data(problem_instance_filepath)
