import time
import copy
import itertools
from z3 import Solver, Real, sat

sleeptime = 0

def check_probs(elts, probs):
    if not elts:
        print("Error: The input was empty or invalid.")
        time.sleep(sleeptime)
        return False

    if not probs:
        print("Error: The input was empty or invalid.")
        time.sleep(sleeptime)
        return False

    if len(elts) != len(probs):
        print("Error: The number of elements and probabilities must match.")
        time.sleep(sleeptime)
        return False

    for i in probs:
        if i < 0:
            print("Error: Probabilities must be non-negative.")
            time.sleep(sleeptime)
            return False

    if abs(sum(probs) - 1.0) > 1e-6:
        print("Error: The probabilities must sum to 1.")
        time.sleep(sleeptime)
        return False
    
    return True

def bayes_rule(prec_partition, neg, is_prec_bayes):

    if not is_prec_bayes:
        rem = False
        for i in prec_partition:
            if i[0] == neg:
                prec_partition.remove(i)
                rem = True
        if rem:
            newtot = 0
            for i in prec_partition:
                newtot += i[1]

            for i in prec_partition:
                if newtot == 0:
                    newtot = 1e-6
                i[1] = i[1] / newtot
    else:
        rem = False
        for i in prec_partition:
            if (neg + "=1") in i[0]:
                prec_partition.remove(i)
                rem = True
        if rem:
            newtot = 0
            for i in prec_partition:
                newtot += float(i[1])

            for i in prec_partition:
                if newtot == 0:
                    newtot = 1e-6
                i[1] = str(float(i[1]) / newtot)
    

    return prec_partition

def inconsistent(belief_type, b1, b2):

    if belief_type == 0:
        for bel1, prob1 in b1:
            for bel2, prob2 in b2:
                if bel1 == bel2 and prob1 != prob2:
                    return True

        return False

    elif belief_type == 1:
        if b1[0] == b2[0]:
            for i in b1[1]:
                for j in b2[1]:
                    if i[0] == j[0] and i[1] != j[1]:
                        return True

        return False

    else:
        print("This should not happen.")
        return True
    

class Beliefs:
    def __init__(self):
        self.fst = [] # precise partitions [['elt', prob], ...]
        self.snd = [] # precise entailments [['ant', prec_partition], ...]

    def __str__(self):
        return [self.fst, self.snd].__str__()

class Believer:
    def __init__(self):
        self.beliefs = Beliefs()
        self.beliefs_solver = Solver()

    def add_rule_out(self, belief_type, new_belief):
    
        if belief_type == 0:
            for i in self.beliefs.fst:
                if inconsistent(0, i, new_belief):
                    self.beliefs.fst.remove(i)
            self.beliefs.fst.append(new_belief)

        elif belief_type == 1:
            for i in self.beliefs.snd:
                if inconsistent(1, i, new_belief):
                    self.beliefs.snd.remove(i)
            self.beliefs.snd.append(new_belief)

        else:
            print("Error: Invalid belief type.")
            return

    def add_to_beliefs(self, addition_type):

        if addition_type == "1":
            self.add_prec_partition()
        elif addition_type == "2":
            self.add_prec_entailment()
        elif addition_type == "3":
            return
        else:
            print("Error: Invalid addition type.")
            return

    def add_prec_partition(self):

        partition = input("Enter the precise partition elements separated by commas: ")
        elts = [elt.strip() for elt in partition.split(",")]

        try:
            probs = input("Enter the probabilities for each element in decimal format separated by commas: ")
            probs = [float(prob.strip()) for prob in probs.split(",")]
        except ValueError:
            print("Error: Invalid probability format.")
            time.sleep(sleeptime)
            return

        check = check_probs(elts, probs)
        if not check:
            return

        new_prec_part = [list(item) for item in zip(elts, probs)]

        self.beliefs.fst.append(new_prec_part)
        print("Precise partition added successfully.")

        self.beliefs_solver.push()

        for elt, prob in new_prec_part:
            self.beliefs_solver.add(Real(elt) == prob)

        if self.beliefs_solver.check() == sat:
            print("The belief set is consistent.")
        else:
            print("The belief set is inconsistent. Removing the last addition.")
            self.beliefs.fst.pop()
            self.beliefs_solver.pop()
            time.sleep(sleeptime)
    
    def add_prec_entailment(self):

        ant = input("Enter the antecedent to be negated: ").strip()
        ant = "-" + ant

        cons = input("Enter the partition elements of the consequent separated by commas: ")
        cons_elts = [elt.strip() for elt in cons.split(",")]
    
        try:
            cons_probs = input("Enter the probabilities for each element of the consequent in decimal format separated by commas: ")
            cons_probs = [float(prob.strip()) for prob in cons_probs.split(",")]
        except ValueError:
            print("Error: Invalid probability format.")
            time.sleep(sleeptime)
            return
        
        check = check_probs(cons_elts, cons_probs)
        if not check:
            return

        for i, j in zip(cons_elts, cons_probs):
            if i == ant[1:] and j > 0:
                print("Error: That which is negated in the antecedent cannot be part of the consequent.")
                time.sleep(sleeptime)
                return

        newpart = [list(item) for item in zip(cons_elts, cons_probs)]
        newbel = [ant, newpart]

        bad_ant = False
        consistent = True
        for bel in self.beliefs.snd:
            if inconsistent(1, bel, newbel):
                bad_ant = True
                
                for part in self.beliefs.fst:
                    for elt, prob in part:
                        if elt == bel[0][1:] and prob < 1: #check for consistency, conditional on antecedent featuring in a belief
                            consistent = False

        if consistent and not bad_ant:
            self.beliefs.snd.append(newbel)
        
            print("Precise entailment added successfully.")
            time.sleep(sleeptime)
        elif consistent and bad_ant:
            self.beliefs.snd.append(newbel)

            print("Precise entailment added successfully. However, the antecedent now entails a contradiction, and so its negation is confirmed.")
            self.beliefs.fst.append([[ant[1:], 1.0]])

            time.sleep(sleeptime)
        else:
            print("The precise entailment is inconsistent with existing beliefs, and will not be added.")
            time.sleep(sleeptime)

    def update_beliefs(self, neg):

        old_beliefs = copy.deepcopy(self.beliefs)
        
        for i in self.beliefs.fst:
            for j in i:
                if j[0] == neg and j[1] == 1:
                    self.beliefs.fst.remove(i)
                    
            i = bayes_rule(i, neg, False)

        for i in self.beliefs.snd:

            to_rem = False

            for j in i[1]:
                if j[0] == neg and j[1] == 1:
                    self.add_rule_out(0, [[i[0][1:], 1.0]]) 
                    # if the consequent is ruled out so is the antecedent; but the antecedent is a negation
                    # so the proposition within is confirmed (classical logic); [1:] removes the "-"
                    to_rem = True

            i[1] = bayes_rule(i[1], neg, False)

            if i[0] == "-" + neg:
                self.add_rule_out(0, i[1])
            
        # reset system of linear inequalities/equations unless inconsistent
        self.beliefs_solver.push()

        self.beliefs_solver.reset()
        for part in self.beliefs.fst:
            for elt, prob in part:
                self.beliefs_solver.add(Real(elt) == prob)

        if self.beliefs_solver.check() == sat:
            print("Beliefs updated successfully.")
            time.sleep(sleeptime)
        else:
            print("The belief set is inconsistent after the update. Reverting to previous beliefs.")
            self.beliefs = old_beliefs
            self.beliefs_solver.pop()
            time.sleep(sleeptime)

            
class Bayesian:
    def __init__(self):
        self.prior = [] # prior should be a propositions taken to be possible
        self.constraints = [] # constraints should be a list of strings representing inequalities/equalities fixing probability values
        self.constraints_solver = Solver()
        self.vars = {} # dictionary mapping prior elements to z3 Real variables
        
        self.precise = False
        self.precise_prior = [] # precise prior should be a precise partition [['elt', prob], ...]

    def beliefs_to_prior(self, beliefs):

        possible_propns = set()
        for part in beliefs.fst:
            for elt, prob in part:
                if prob > 0:
                    possible_propns.add(elt)
        
        for ent in beliefs.snd:
            if ent[0][1:] in possible_propns:
                for elt, prob in ent[1]:
                    if prob > 0:
                        possible_propns.add(elt)

        indicator_vars = []
        for p in possible_propns:
            indicator_vars.append([p + "=0", p + "=1"])

        all_combinations = [str(p) for p in itertools.product(*indicator_vars)]

        for part in beliefs.fst:
            for comb in copy.deepcopy(all_combinations):
                imp = False
                counter = 0
                for [elt, prob] in part:
                    if (elt + "=1") in comb:
                        counter += 1
                    if prob == 0 and (elt + "=1") in comb:
                        imp = True
                if counter != 1 or imp:
                    all_combinations.remove(comb)
        
        for ent in beliefs.snd:
            ant = ent[0][1:]
            
            for comb in copy.deepcopy(all_combinations):
                imp = False
                counter = 0
                for [elt, prob] in ent[1]:
                    if (elt + "=1") in comb:
                        counter += 1
                        if prob == 0 and (ant + "=0") in comb:
                            imp = True
                if ((ant + "=0") in comb and counter != 1) or imp:
                    all_combinations.remove(comb)

        self.prior = copy.deepcopy(all_combinations)

        for comb in self.prior:
            self.vars[comb] = Real(comb)

        for comb in self.prior:
            self.constraints_solver.add(self.vars[comb] >= 0)
        self.constraints.append("for any i in prior, P(i) >= 0")

        self.constraints_solver.add(sum([self.vars[comb] for comb in self.prior]) == 1)
        self.constraints.append("sum of all P(i) for i in prior = 1")

        for part in beliefs.fst:
            for elt, prob in part:
                self.constraints_solver.add(sum([self.vars[comb] for comb in self.prior if (elt + "=1") in comb]) == prob)
                self.constraints.append("sum of all P(i) for i in prior where " + elt + " is true = " + str(prob))
        
        for ent in beliefs.snd:
            ant = ent[0][1:]
            for elt, prob in ent[1]:
                self.constraints_solver.add(sum([self.vars[comb] for comb in self.prior if (ant + "=0") in comb and (elt + "=1") in comb]) == prob * sum([self.vars[comb] for comb in self.prior if (ant + "=0") in comb]))
                self.constraints.append("sum of all P(i) for i in prior where " + ant + " is false and " + elt + " is true = " + str(prob) + " * P(-" + ant + ")")

        if self.constraints_solver.check() == sat:
            return True
        else:
            print("The beliefs cannot be converted to a prior.")
            return False

    def become_precise(self):
        sol = self.constraints_solver.model()
        
        temp = []
        for comb in self.prior:
            temp.append([comb, sol[self.vars[comb]].as_decimal(3)])

        self.precise = True
        self.precise_prior = [list(t) for t in set(tuple(i) for i in temp)] # remove duplicates ... not sure why there are any, though

    def posterior(self, neg):
        if not self.precise:
            print("Update for imprecise prior not implemented yet. Would you like to fix a precise prior consistent with the imprecise prior? (y/n)")
            ans = input().strip().lower()
            if ans == 'y':
                self.become_precise()
            if ans == 'n':
                return

        self.precise_prior = bayes_rule(self.precise_prior, neg, True)
        print("Posterior computed successfully.")
        time.sleep(sleeptime)

def print_options():
    print("Select an option by entering a number:")
    time.sleep(sleeptime)
    print("[1] - Add to beliefs")
    print("[2] - Update beliefs")
    print("[3] - Bayesian mode")
    print("[4] - Load a preset")
    print("[5] - Reset beliefs")
    print("[6] - Help")
    print("[7] - Exit")

def print_help():
    print("(To be implemented; probably will just link to website)")
    #TODO   

def print_additions():
    print("Select an addition type by entering a number:")
    print("[1] Add a precise partition")
    print("[2] Add a precise entailment")
    print("[3] Go back")

def load_presets(bel_agent, bayes_agent, bayes):
    print("Which preset would you like to load?")
    time.sleep(sleeptime)
    print("[1] Sleeping Beauty 1")
    print("[2] Sleeping Beauty 2")
    print("[3] Go back")

    selection = input()
    if selection == "1":
        bayes = False
        bel_agent.beliefs.fst = [[['H', 0.5], ['T', 0.5]]]
        bel_agent.beliefs.snd = [['-H', [['T1', 0.5], ['T2', 0.5]]], ['-T', [['H', 1.0], ['T1', 0.0], ['T2', 0.0]]]]
        return bel_agent, bayes_agent, bayes
    elif selection == "2":
        bayes = False
        bel_agent.beliefs.fst = [[['H', 0.5], ['T', 0.5]]]
        bel_agent.beliefs.snd = [['-H', [['T1', 0.5], ['T2', 0.5]]]]
        return bel_agent, bayes_agent, bayes
    elif selection == "3":
        return bel_agent, bayes_agent, bayes
    else:
        return bel_agent, bayes_agent, bayes
        print("Invalid selection.")
