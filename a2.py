# -*- coding: utf-8 -*-
# Assignment 2 - Jared Frank
# Imports for A
from logic import pl_resolution, KB, PropKB, expr, FolKB
# Imports for B
from planning import Action, PlanningProblem, ForwardPlan
from search import astar_search
# Imports for C

""" A2 Part A

    giveFeedback is a function that reads in a student state and returns a feedback message using propositional logic and proof by resolution. The rules
    for how to decide which message to return are given in the assignment description.
    
    studentState:   a String representing a conjunction of five possible symbols: CorrectAnswer, NewSkill, MasteredSkill, CorrectStreak, IncorrectStreak
                    For example, you could call giveFeedback('CorrectAnswer') or giveFeedback('MasteredSkill & CorrectStreak')
    
    feedbackMessage:a String representing one of eight feedback messages (M1 through M8 below). 
    
    Feel free to refactor the code to move M1 through M8 into a class, but the function call and return values should remain as specified below for our grading.


"""

M1 = 'Correct. Keep up the good work!'
M2 = 'Correct. I think you’re getting it!'
M3 = 'Correct. After this problem we can switch to a new problem.'
M4 = 'Incorrect. Keep trying and I’m sure you’ll get it!'
M5 = 'Incorrect. After this problem, we can switch to a new activity.'
M6 = 'Incorrect. The following is the correct answer to the problem.'
M7 = 'Correct.'
M8 = 'Incorrect.'

# Returns the feedback message based on the message that is sent
def giveFeedback(student_state):
    statement_list = [
        "CorrectAnswer ==> (Message1 | Message2 | Message3 | Message7)",
        "~CorrectAnswer ==> (Message4 | Message5 | Message6 | Message8)",
        "(MasteredSkill & ~CorrectAnswer) & (MasteredSkill & CorrectStreak) ==> IsBored",
        "(NewSkill | IncorrectStreak) & CorrectAnswer ==> Message6",
        "(IncorrectStreak & CorrectAnswer) | (NewSkill & CorrectStreak) ==> NeedsEncouragement",
        "NeedsEncouragement & CorrectAnswer ==> Message2",
        "NeedsEncouragement & ~CorrectAnswer ==>  Message4",
        "IsBored ==> Message3 | Message5",
        "(NewSkill & CorrectAnswer) | CorrectStreak ==> Message1"
    ]
    priority_array = ["Message1", "Message2", "Message3", "Message4", "Message5", "Message6", "Message7", "Message8"]
    msg_dict = {"Message1": M1, "Message2": M2, "Message3": M3, "Message4": M4, "Message5": M5, "Message6": M6,
                "Message7": M7, "Message8": M8}
    feedback_msg = "Nothing Entailed"
    knowledge_base = PropKB()
    for s in statement_list:
        knowledge_base.tell(s)

    knowledge_base.tell(expr(student_state))

    # Iterate through all propositions
    for p in priority_array:
        p_expr = expr(p)

        resolution_bool = pl_resolution(knowledge_base, p_expr)
        if resolution_bool:
            print(str(resolution_bool) + " : " + p)
            return "Message: " + msg_dict.get(p)

        else:
            neg_p_expr = expr('~' + p)
            knowledge_base.tell(neg_p_expr)
            print('Adding: ~' + p)
    return feedback_msg

""" A2 Part B
 
    solveEquation is a function that converts a string representation of an equation to a first-order logic representation, and then
    uses a forward planning algorithm to solve the equation. 
    
    equation:   a String representing the equation to be solved. "x=3", "-3x=6", "3x-2=6", "4+3x=6x-7" are all possible Strings.
                For example, you could call solveEquation('x=6') or solveEquation('-3x=6')
    
    plan:   return a list of Strings, where each String is a step in the plan. The Strings should reference the core actions described in the
            Task Domain part of the assignment description.
    
"""

# Parses the input Equation to get the initial string for the PlanningProblem

# Get the left-hand terms
def getLeftTerms(equation):
    left_terms = []
    (left_eq, right_eq) = equation.split('=')
    operator_pos = 0
    while operator_pos != -1:
        plus_operator_pos = str(left_eq).rfind('+')
        minus_operator_pos = str(left_eq).rfind('-')
        operator_pos = max(plus_operator_pos, minus_operator_pos)
        if operator_pos == -1:
            left_terms.append(str(left_eq[0:len(left_eq)]))
        else:
            left_terms.append(str(left_eq)[operator_pos:len(left_eq)])
            left_eq = left_eq[0:operator_pos]
    return left_terms

# Get the right-hand terms
def getRightTerms(equation):
    right_terms = []
    (left_eq, right_eq) = equation.split('=')
    operator_pos = 0
    while operator_pos != -1:
        plus_operator_pos = str(right_eq).rfind('+')
        minus_operator_pos = str(right_eq).rfind('-')
        operator_pos = max(plus_operator_pos, minus_operator_pos)
        if operator_pos == -1:
            right_terms.append(str(right_eq[0:len(right_eq)]))
        else:
            right_terms.append(str(right_eq)[operator_pos:len(right_eq)])
            right_eq = right_eq[0:operator_pos]

    return right_terms

# Combine both sides of terms into initial state string
def getInitialString(left_terms, right_terms):
    #left_terms = list(filter(None, left_terms))
    #right_terms = list(filter(None, right_terms))

    # Begin Planning Problem
    # Create initial string for Planning Problem
    initial_str = ''
    for term in left_terms:
        if term.find('+') != -1:
            term = term.replace('+', '')
        if term.find('x') != -1:
            # If the term is a variable
            if term == 'x':
                term = '1'
            elif term == '-x':
                term = '-1'
            elif term == '+':
                term = '1'
            term = term.replace('x', '')
            initial_str += " VarLeft(" + str(term) + ") &"
        else:
            # Term is a constant
            initial_str += " ConstLeft(" + str(term) + ") &"
    for t in right_terms:
        if t.find('+') != -1:
            t = t.replace('+', '')
        if t.find('x') != -1:
            # If the term is a variable
            if t == 'x':
                t = '1'
            elif t == '-x':
                t = '-1'
            elif t == '+x':
                t = '-1'
            t = t.replace('x', '')
            initial_str += " VarRight(" + str(t) + ") &"
        else:
            # Term is a constant
            initial_str += " ConstRight(" + str(t) + ") &"
    initial_str = initial_str[1:-2]
    return initial_str

# Calculates the divisor for the end of the problem based on the terms in the equation
def calcDivisor(lht, rht):
    divisor_val = 0
    for lt in lht:
        if 'x' in lt:
            lt = lt.replace('x', '')
            if '+' in lt:
                lt = lt.replace('+', '')
            divisor_val += int(lt)
    for r in rht:
        if 'x' in r:
            r = r.replace('x', '')
            if '+' in r:
                r = r.replace('+', '')
                r = '-' + r
            elif '-' in r:
                r = r.replace('-', '')
            divisor_val += int(r)
    return divisor_val

# Parse the output solution into the correct form
def parseSolution(solution_arr, left_terms, right_terms):
    parsed_solution = []
    for actions in solution_arr:
        actions = str(actions)
        # If the action is to Add a var
        if actions.find("addVar") != -1:
            val = actions[7]
            if actions[6] == '-':
                val = '-' + val
            val += 'x'
            parsed_solution.append('add ' + str(val))
        # If the action is to Add a const
        elif actions.find('addConst') != -1:
            val = actions[9]
            if actions[8] == '-':
                val += '-'
            parsed_solution.append('add ' + str(val))
        # If the action is to combine the RHS
        elif actions.find('combineRightConst') != -1:
            parsed_solution.append('combine RHS constant terms')
        # If the action is to combine the LHS
        elif actions.find('combineLeftVar') != -1:
            parsed_solution.append('combine LHS variable terms')
    divisor = calcDivisor(left_terms, right_terms)
    parsed_solution.append('divide ' + str(divisor))
    return parsed_solution

SAMPLE_EQUATION = '9x+2x=4+1'
SAMPLE_ACTION_PLAN = ['add 2', 'combine RHS constant terms', 'divide 3']

# Solve the equation and return the steps
def solveEquation(equation):
    # Get the string representing the initial state
    left_terms = getLeftTerms(equation)
    right_terms = getRightTerms(equation)
    left_terms = list(filter(None, left_terms))
    right_terms = list(filter(None, right_terms))
    initial_str = getInitialString(left_terms, right_terms)
    terms_list = initial_str.split("&")
    count_const = 0
    count_var = 0
    for x in terms_list:
        if x.find('Const') != -1:
            count_const += 1
        if x.find('Var') != -1:
            count_var += 1

    # There is only a single var
    if count_var == 1:
        terms_list.append(" SingleVar()")
    elif count_var == 2:
        terms_list.append(" TwoVars()")

    # There is only a single const
    if count_const == 1:
        terms_list.append(" SingleConst()")
    elif count_const == 2:
        terms_list.append(" TwoConsts()")

    # Create initial string again
    initial_str = ' &'
    initial_str = initial_str.join(terms_list)
    print(initial_str)
    print()
    # Create the planning problem
    planning_prob = PlanningProblem(initial=initial_str,
                                    goals='Solved()',
                                    actions=[Action('addVar(a)',
                                                    precond='VarRight(a)',
                                                    effect='VarLeft(a) & ~VarRight(a)',),
                                             # Add a constant to right side from left
                                             Action('addConst(b)',
                                                    precond='ConstLeft(b)',
                                                    effect='ConstRight(b) & ~ConstLeft(b)',),
                                             # Combine two consts on the right and replace all with SingleConst()
                                             Action('combineRightConstTwoTerms(a, b)',
                                                    precond='ConstRight(a) & ConstRight(b) & TwoConsts()',
                                                    effect='~ConstRight(a) & ~ConstRight(b) & SingleConst()'),
                                             # Combine three consts on the right and replace all with SingleConst()
                                             Action('combineRightConstThreeTerms(a, b, c)',
                                                    precond='ConstRight(a) & ConstRight(b) & ConstRight(c)',
                                                    effect='~ConstRight(a) & ~ConstRight(b) & ~ConstRight(c) & SingleConst()'),
                                             Action('combineLeftVarTwoTerms(a, b)',
                                                    precond='VarLeft(a) & VarLeft(b) & TwoVars()',
                                                    effect='~VarLeft(a) & ~VarLeft(b) & SingleVar()'),
                                             Action('combineLeftVarThreeTerms(a, b, c)',
                                                    precond='VarLeft(a) & VarLeft(b) & VarLeft(c)',
                                                    effect='~VarLeft(a) & ~VarLeft(b) & ~VarLeft(c) & SingleVar()'),
                                             # Combine two consts on right where both have duplicate coefficients
                                             # Action('combineRightDupsTwo(a)',
                                             #        precond='ConstRight(a) & ConstRight(a)',
                                             #        effect='~ConstRight(a) & ~ConstRight(a) & ConstRight(b) & SingleConst()'),
                                             # # Combine three consts on right where all have duplicate coefficients
                                             # Action('combineRightDupsThree(a)',
                                             #        precond='ConstRight(a) & ConstRight(a) & ConstRight(a)',
                                             #        effect='~ConstRight(a) & ~ConstRight(a) & ~ConstRight(a) & ConstRight(b) & SingleConst()'),
                                             # Divide the SingleVar on left and SingleConst on right return Solved()
                                             Action('divideNoDup()',
                                                    precond='SingleConst() & SingleVar()',
                                                    effect='Solved() & ~SingleConst() & ~SingleVar()',),
                                             # Divide SingleVar on left and SingleConst on right with equal coefficients and return Solved()
                                             Action('divideDup(a)',
                                                    precond='SingleConst() & SingleVar()',
                                                    effect='Solved() & ~SingleConst() & ~SingleVar()'),
                                             ])
    fwd_plan = ForwardPlan(planning_prob)
    solution_str = astar_search(fwd_plan).solution()
    return parseSolution(solution_str, left_terms, right_terms)

""" A2 Part C

    predictSuccess is a function that takes in a list of skills students have and an equation to be solved, and returns the skills
    students need but do not currently have in order to solve the skill. For example, if students are solving the problem 3x+2=8, and have S7 and S8, 
    they would still need S4 and S5 to solve the problem.
    
    current_skills: A list of skills students currently have, represented by S1 through S9 (described in the assignment description)
    
    equation:   a String representing the equation to be solved. "x=3", "-3x=6", "3x-2=6", "4+3x=6x-7" are all possible Strings.
                For example, you could call solveEquation('x=6') or solveEquation('-3x=6')
    
    missing_skills: A list of skills students need to solve the problem, represented by S1 through S9.
    
"""
CURRENT_SKILLS = ['S8', 'S9']
EQUATION = '3x-2=6'
SAMPLE_MISSING_SKILLS = ['S4', 'S5']


def calcCombineVars(terms):
    total = 0
    for t in terms:
        if 'x' in t:
            t = t.replace('x', '')
            total += int(t)

    return total

def predictSuccess(current_skills, equation):
    curr_skills_KB = FolKB()
    required_skills_KB = FolKB()
    required_skills = {}
    # Create KnowledgeBase for current skills that exist
    for skill in current_skills:
        curr_skills_KB.tell(expr(skill))

    steps_for_solving = solveEquation(equation)
    lht = getLeftTerms(equation)
    rht = getRightTerms(equation)
    divisor = calcDivisor(lht, rht)
    rht_var_combine = calcCombineVars(rht)
    lht_var_combine = calcCombineVars(lht)

    for step in steps_for_solving:
        if 'addVar' in step:
            if step[6] == '-':
                required_skills.add('S2')
            else:
                required_skills.add('S1')
        elif 'addConst' in step:
            if step[9] == '-':
                required_skills.add('S4')
            else:
                required_skills.add('S3')
        elif 'divide' in step:
            if divisor > 0:
                required_skills.add('S5')
            else:
                required_skills.add('S6')
        elif 'combineRightConst' | 'combineRightConstTwo' in step:
            required_skills.add('S9')
        elif 'combineLeftVar':
            if (rht_var_combine > 0) | (lht_var_combine > 0):
                required_skills.add('S7')
            else:
                required_skills.add('S8')

    for sk in required_skills:
        required_skills_KB.tell(expr(sk))
    for curr_sk in curr_skills_KB.clauses:
        required_skills_KB.retract(curr_sk)
    
    missing_skills = required_skills_KB.clauses
    return missing_skills


""" A2 Part D

    stepThroughProblem is a function that takes a problem, a student action, and a list of current student skills, and returns
    a list containing a feedback message to the student and their updated list of skills.
    
    equation: a String representing the equation to be solved. "x=3", "-3x=6", "3x-2=6", "4+3x=6x-7" are all possible Strings.
    
    action: an action in the task domain. For example: 'add 2', 'combine RHS constant terms', 'divide 3'
    
    current_skills: A list of skills students currently have, represented by S1 through S9 (described in the assignment description)
    
    feedback_message: A feedback message chosen correctly from M1-M9.
    
    updated_skills: A list of skills students have after executing the action.
    
"""
ACTION = 'add -2'
UPDATED_SKILLS = ['S8', 'S9', 'S4']


def stepThroughProblem(equation, action, current_skills):
    feedback_message = M1
    updated_skills = UPDATED_SKILLS
    return [feedback_message, updated_skills]


if __name__ == '__main__':
    # Testing Part A
    #print(giveFeedback("CorrectAnswer & IncorrectStreak"))

    # Testing Part B
    #print(SAMPLE_EQUATION)
    #print(solveEquation(SAMPLE_EQUATION))

    # Testing for Part C
    predictSuccess(CURRENT_SKILLS, EQUATION)