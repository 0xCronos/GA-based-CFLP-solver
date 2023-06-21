import random
from amplpy import AMPL


class GeneticAlgorithm:
    """ Implementation of genetic algorithm using selection by tournament, mutation and crossover """
    n_population = 24
    crossover_rate = 0.9

    def __init__(self, n_iter, n_bits=None):
        self.n_iter = n_iter
        self.n_bits = n_bits

        if self.n_bits:
            self.mutation_rate = self.calculate_mutation_rate(n_bits)
        else:
            self.mutation_rate = None

    def run(self, ampl: AMPL):
        found_solutions = []
        best_solutions_by_generation = []

        # generates initial population of random binary vectors
        population = [[random.randint(0, 1) for _ in range(
            self.n_bits)] for _ in range(self.n_population)]

        # get ampl binary vector parameter x
        x = ampl.get_parameter('x')

        # get score of first parent (F.O)
        x.set_values(population[0])
        best_x = x

        ampl.solve()
        best_score = ampl.get_value('Total_Cost')

        # check if solution was found
        if ampl.get_value('solve_result') == 'solved':
            best_solutions_by_generation.append([best_x, best_score])

        # start generations
        for generation in range(self.n_iter):
            print(f'\n\n[INFO] generation: {generation+1}')

            # evaluate all candidates in the current population
            scores = []
            for c in population:
                x.set_values(c)
                ampl.solve()

                score = ampl.get_value('Total_Cost')

                # check if solution was found
                if ampl.get_value('solve_result') == 'solved':
                    found_solutions.append([c, score])
                    scores.append(score)

            # check if non solutions found yet
            if not scores:
                continue

            # check for new best solution
            for i in range(len(scores)):
                if scores[i] < best_score:
                    best_x, best_score = population[i], scores[i]

            best_solutions_by_generation.append([best_x, best_score])

            # tournament based selection
            selected = [self.__selection(population, scores)
                        for _ in range(self.n_population)]

            # create next generation
            children = []
            for i in range(0, self.n_population, 2):
                # get a pair of parents
                p1, p2 = selected[i], selected[i+1]

                for c in self.__crossover(p1, p2):
                    self.__mutation(c)
                    children.append(c)

            population = children

        if found_solutions and best_solutions_by_generation:
            return best_x, best_score, found_solutions, best_solutions_by_generation
        else:
            return None, None, found_solutions, best_solutions_by_generation

    def calculate_mutation_rate(self, n_bits):
        return 1.0 / float(n_bits)

    def __selection(self, population, scores, k=3):
        # first random selection
        best_idx = random.randrange(0, len(population))

        # get k random indexes
        for idx in [random.randrange(0, len(population)) for _ in range(k-1)]:

            # check if better
            if scores[idx] < scores[best_idx]:
                best_idx = idx

        return population[best_idx]

    def __crossover(self, p1, p2):
        c1, c2 = p1.copy(), p2.copy()

        if random.uniform(0, 1) < self.crossover_rate:
            pt = random.randint(1, len(p1) - 2)

            c1 = p1[:pt] + p2[pt:]
            c2 = p2[:pt] + p1[pt:]

        return [c1, c2]

    def __mutation(self, bitstring):
        for i in range(len(bitstring)):
            if random.uniform(0, 1) < self.mutation_rate:
                bitstring[i] = 1 - bitstring[i]
