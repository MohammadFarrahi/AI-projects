import random
from time import time

INPUT_FIELD = [[] for _ in range(9)]        # input sudoku field
INDEXS = [i for i in range(9)]              # list of 0 to 8 
COMB_INDEXS = [(i,j) for i in range(9) for j in range(i+1, 9)]      # orderd combination of each 2 indexs ; (0,1) (0,2) (0,3) ...


# condidate model containing chromosome and its fitness
class Condidate:
    def __init__(self):
        self.solution = [[0 for _ in range(9)] for _ in range(9)]       # solution or chromosome containing 9 gens(rows)
        self.fitness = 0
    
    def calculate_fitness(self):
        self.fitness = 0
        for col in zip(*self.solution):
            self.fitness += len(set(col))       # adding size of unique nubmbers in each col
        
        for i in range(0, 9, 3):
            for j in range(0, 9, 3):
                block_values = []
                block_values.extend(self.solution[i][j:j+3])
                block_values.extend(self.solution[i+1][j:j+3])
                block_values.extend(self.solution[i+2][j:j+3])
                self.fitness += len(set(block_values))          # adding size of unique nubmbers in each block

    def apply_mutation(self, Pm, gen_mutate_count=9):       # perfoming a mutation on determined number of random gens
        is_mutated = False
        gen_indexs = random.sample(INDEXS, gen_mutate_count)
        for gen_ind in gen_indexs:
            if random.random() > Pm:
                continue
            if self._mutate_gen(gen_ind):
                is_mutated = True
        if is_mutated: self.calculate_fitness()
        return is_mutated

    def _mutate_gen(self, ind):
        """ loops through COMB_INDEXS and finds two col indexes in row(gen) that their values is not fixed and if their swaping will cause no conflicts, 
            then swap their values and returns. if there is no combination whch satisfy conditions, returns on fail"""
        
        gen = self.solution[ind]
        is_mutated = False
        for cell_inds in COMB_INDEXS:
            if INPUT_FIELD[ind][cell_inds[0]] or INPUT_FIELD[ind][cell_inds[1]]: continue
            if (not (self._is_value_block_conflict(gen[cell_inds[0]], ind, cell_inds[1]) or self._is_value_col_conflict(gen[cell_inds[0]], ind, cell_inds[1])) and
                not (self._is_value_block_conflict(gen[cell_inds[1]], ind, cell_inds[0]) or self._is_value_col_conflict(gen[cell_inds[1]], ind, cell_inds[0]))):
                is_mutated = True
                gen[cell_inds[0]], gen[cell_inds[1]] = gen[cell_inds[1]], gen[cell_inds[0]]
                break
        return is_mutated
    
    def _is_value_block_conflict(self, value, row, col):
        for i in range(row//3, row//3+3):
            if i == row: continue
            for j in range(col//3, col//3+3):
                if self.solution[i][j] == value: True
        return False
    
    def _is_value_col_conflict(self, value, row, col):
        for i in range(9):
            if i == row: continue
            if self.solution[i][col] == value:
                return True
        return False
    
    def print(self):
        for row in self.solution:
            print(*row, sep=' ')
    

class Population:
    def __init__(self):
        self.condidates = []
        self.possible_values = [[[] for _ in range(9)] for _ in range(9)]       # possible for each cell in field according to static values given by input
        self.set_possible_values()

    def set_possible_values(self):
        row_values = []
        col_values = []
        for row in INPUT_FIELD:
            row_values.append(set(row))
        for col in zip(*INPUT_FIELD):
            col_values.append(set(col))
        for i in range(0, 9, 3):
            for j in range(0, 9, 3):
                block_values = set()
                block_values.update(INPUT_FIELD[i][j:j+3])
                block_values.update(INPUT_FIELD[i+1][j:j+3])
                block_values.update(INPUT_FIELD[i+2][j:j+3])
                for ii in range(i, i+3):
                    for jj in range(j, j+3):
                        if INPUT_FIELD[ii][jj] != 0: continue
                        self.possible_values[ii][jj] = [x for x in range(1,10) if x not in block_values
                                                                                and x not in row_values[ii]
                                                                                and x not in col_values[jj]]
    
    def generate_inital(self, pop_size):
        for _ in range(pop_size):
            self.condidates.append(self._generate_random_condidate())

    def _generate_random_condidate(self):
        condidate = Condidate()
        for i in range(9):
            for j in range(9):
                if INPUT_FIELD[i][j] != 0:
                    condidate.solution[i][j] = INPUT_FIELD[i][j]
                    continue
                condidate.solution[i][j] = self.possible_values[i][j][random.randint(0, len(self.possible_values[i][j])-1)]
            while len(set(condidate.solution[i])) != 9:
                for j in range(9):
                    if(INPUT_FIELD[i][j] == 0):
                        condidate.solution[i][j] = self.possible_values[i][j][random.randint(0, len(self.possible_values[i][j])-1)]

        condidate.calculate_fitness()
        return condidate

    def sort(self):
        self.condidates.sort(key=lambda el: el.fitness, reverse=True)

    def get_fitness(self):
        return [condidate.fitness for condidate in self.condidates]

    def get_mating_pool(self, selection_rate, size):
        mating_pool = []
        for _ in range(size):
            mating_pool.append(tournament_selection(self.condidates, selection_rate))
        return mating_pool


# instead of roullete wheel, we use binary tournament selection for mating pool sampling
def tournament_selection(condidates, selection_rate):
    ind1, ind2 = random.randint(0, len(condidates)-1), random.randint(0, len(condidates)-1)
    while ind1 == ind2:
        ind1, ind2 = random.randint(0, len(condidates)-1), random.randint(0, len(condidates)-1)
    
    fittest, weakest = condidates[ind1], condidates[ind2]
    fit1, fit2 = fittest.fitness, weakest.fitness
    if fit1 < fit2:
        fittest , weakest = weakest, fittest
    if random.random() > selection_rate: return weakest
    return fittest


def apply_crossover(p1, p2, Pc):        # perfoming a uniform crossover with probability of Pc
    if random.random() > Pc:
        return p1, p2, False

    is_crossed = False
    ch1, ch2 = Condidate(), Condidate()
    for gen_ind in INDEXS:
        if random.random() <= 0.5:
            is_crossed = True
            ch1.solution[gen_ind], ch2.solution[gen_ind] = p2.solution[gen_ind].copy(), p1.solution[gen_ind].copy()
        else:
            ch1.solution[gen_ind], ch2.solution[gen_ind] = p1.solution[gen_ind].copy(), p2.solution[gen_ind].copy()
    ch1.calculate_fitness()
    ch2.calculate_fitness()
    return ch1, ch2, is_crossed


def apply_GA():
    exe_time = time()

    #hyper parameters
    TIME_OUT = 3
    POP_SIZE = 500
    ELITE_SIZE = int(POP_SIZE * 5/100) if int(POP_SIZE * 5/100) % 2 == 0 else int(POP_SIZE * 5/100)-1       # elite and population size must be even
    MIN_FITNESS_TO_TERMINATE = 9*9*2
    SELECTION_RATE = 0.7
    RESET_COUNT = 50
    P_C = 0.69
    MAX_PC = 0.89
    P_M = 1/9
    MIN_PM = 1/POP_SIZE
    TO_MUTATE_GEN_NUM = 9
    
    # dynamic pc and pm given to crossove and mutaion operations
    dynamic_pc = P_C
    success_cross_num = 0
    dynamic_pm = P_M
    success_mutate_num = 0
    better_fitness_count = 0

    best_answer_sofar = Condidate()

    population = Population()
    population.generate_inital(POP_SIZE)
    population.sort()

    count = 0
    while time() - exe_time < TIME_OUT*60:
        # looking for answer
        if best_answer_sofar.fitness < population.condidates[0].fitness:
            best_answer_sofar.solution = population.condidates[0].solution
            best_answer_sofar.fitness = population.condidates[0].fitness
            if best_answer_sofar.fitness >= MIN_FITNESS_TO_TERMINATE:
                return best_answer_sofar, True
        # if you want to see condidates' fitnesses and best solution in each sycle, uncomment following 3 lines
        # print(population.get_fitness())
        # population.condidates[0].print()
        # print('count:', count, "pc:", dynamic_pc, "pm:", dynamic_pm, '\n----------------------')
        
        # adding elite condidates and geting matinng pool
        next_pop = population.condidates[0:ELITE_SIZE]
        elite_fitness = [condidate.fitness for condidate in next_pop]
        mating_pool = population.get_mating_pool(SELECTION_RATE, POP_SIZE - ELITE_SIZE)
        # crossover applying to 2 parent from mating pool
        for ind in range(0, len(mating_pool), 2):
            ch1, ch2, success =  apply_crossover(mating_pool[ind], mating_pool[ind+1], dynamic_pc)
            #if new children did not generate and if parents are from elite condidate, choose from condidates with bad fitness(for diversity)
            if not success:
                success_cross_num += 1
                if ch1.fitness in elite_fitness:
                    next_pop.append(population.condidates[random.randint(int(POP_SIZE*0.1), POP_SIZE-1)])
                else:
                    next_pop.append(ch1)
                if ch2.fitness in elite_fitness:
                    next_pop.append(population.condidates[random.randint(int(POP_SIZE*0.1), POP_SIZE-1)])
                else:
                    next_pop.append(ch2)
            else:
                next_pop.append(ch1)
                next_pop.append(ch2)
        if success_cross_num / (len(mating_pool) / 2) < dynamic_pc:         # if crossover doesn't work with determined proportion, increase pc
            dynamic_pc = min(MAX_PC, dynamic_pc / 0.99)
        success_cross_num = 0
        # mutaion applying on new populaion except elite condidates from previous populaiton
        for ind in range(ELITE_SIZE, POP_SIZE):
            condidate = next_pop[ind]
            old_fitnnes = condidate.fitness
            if condidate.apply_mutation(dynamic_pm, TO_MUTATE_GEN_NUM):
                success_mutate_num += 1
                if condidate.fitness > old_fitnnes:
                    better_fitness_count +=1
        # analyzing mutaion operation and change pm for next cycle
        if success_mutate_num:
            if better_fitness_count / success_mutate_num < 0.3:
                dynamic_pm = max(MIN_PM, dynamic_pm * 0.997)
        else: 
            dynamic_pm = P_M
        success_mutate_num, better_fitness_count = 0, 0
        # new population
        population.condidates = next_pop
        population.sort()
        # checking if population is stuck in local minimum and reseting if threshold(RESET_COUNT) is triggerd
        if len(set(population.get_fitness()[0:max(3,int(ELITE_SIZE*0.5))])) == 1:       
            count += 1
        if count > RESET_COUNT:
            population.generate_inital(POP_SIZE)
            population.sort()
            dynamic_pc = P_C
            dynamic_pm = P_M
            count = 0
    
    return best_answer_sofar, False


if __name__ == '__main__':
    #reading input
    for i in range(9):
        INPUT_FIELD[i] = list(map(int, input().split()))

    exe = time()
    answer, status = apply_GA()
    exe = time() - exe
    print('*************************************')
    if status:
        print('answer found!!')
    else:
        print('time out. best possible answer found:')
    print("fitness(Number of unique numbers in cols and blocks (max=162)):", answer.fitness)
    answer.print()
    print("exe time(s):", exe)