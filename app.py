import time

import micropip
await micropip.install(
    "https://pyscript.net/wheels/z3_solver-4.12.1.0-cp311-cp311-emscripten_3_1_32_wasm32.whl"
)

from z3 import Solver, Real, sat

from helper import *

bayes = False

sleeptime = 0

print("Hello, welcome to Statistical Inference Software (SIS).")
time.sleep(sleeptime)

bel_agent = Believer()
bayes_agent = Bayesian()

while True:
    print("Bayesian mode:", bayes)

    if not bayes:
        print("Current belief set:", bel_agent.beliefs)
    else:
        if bayes_agent.precise:
            print("Current prior (precise):", bayes_agent.precise_prior)
        else:
            print("Current prior:", bayes_agent.prior)
            print("Current constraints:", bayes_agent.constraints)
    time.sleep(sleeptime)

    print_options()
    selection = input()

    if selection == "1":

        if bayes:
                print("There is no procedure for adding to a Bayesian prior.")
                time.sleep(sleeptime)
                continue

        print_additions()
        addition_type = input()
        bel_agent.add_to_beliefs(addition_type)
        
        time.sleep(sleeptime)
                
    elif selection == "2":
        
        print("Enter the proposition which has been negated: ")
        neg = input().strip()

        if bayes:
            bayes_agent.posterior(neg)
        else:
            bel_agent.update_beliefs(neg)
        time.sleep(sleeptime)
    
    elif selection == "3":

        if bayes == True:
            print("Reset beliefs to exit Bayesian mode")            
        else:
            if bayes_agent.beliefs_to_prior(bel_agent.beliefs):
                bayes = True
                print("Beliefs successfully converted to prior.")
                time.sleep(sleeptime)
                print("Prior:", bayes_agent.prior)
                print("Constraints:", bayes_agent.constraints)
                time.sleep(sleeptime)
                print("Would you like to fix a consistent precise prior now? (y/n)")
                fix_precise = input().strip().lower()
                if fix_precise == 'y':
                    bayes_agent.become_precise()
                    print("Precise prior fixed successfully.")
                else:
                    print("Continuing with imprecise prior.")
        time.sleep(sleeptime)
    
    elif selection == "4":
        bel_agent, bayes_agent, bayes = load_presets(bel_agent, bayes_agent, bayes)
        time.sleep(sleeptime)

    elif selection == "5":
        bel_agent = Believer()
        bayes_agent = Bayesian()
        bayes = False
        print("Beliefs have been reset.")
        time.sleep(sleeptime)

    elif selection == "6":
        print_help()
        time.sleep(sleeptime)

    elif selection == "7":
        print("Goodbye!")
        break

    else:
        print("Input invalid, please try again.")
        time.sleep(sleeptime)
