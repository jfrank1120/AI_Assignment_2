# -*- coding: utf-8 -*-
# Assignment 2 - Jared Frank
from logic import pl_resolution, KB, PropKB, expr

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


def giveFeedback(student_state):
    statement_list = [
        "CorrectAnswer ==> (Message1 | Message2 | Message3 | Message7)",
        "~CorrectAnswer ==> (Message4 | Message5 | Message6 | Message8)",
        "(MasteredSkill & IncorrectAnswer) | (MasteredSkill & CorrectStreak) ==> IsBored",
        "NewSkill | IncorrectStreak ==> Message6",
        "(IncorrectStreak & CorrectAnswer) | (NewSkill & CorrectStreak) ==> NeedsEncouragement",
        "NeedsEncouragement ==> Message2 | Message4",
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

    list_of_propositions = student_state.split('&')
    for prop in list_of_propositions:
        prop = prop.strip()
        knowledge_base.tell(prop)

    print("CLAUSES:")
    for c in knowledge_base.clauses:
        print(c)

    # Iterate through all propositions
    for p in priority_array:
        p_expr = expr(p)

        resolution_bool = pl_resolution(knowledge_base, p_expr)
        print(resolution_bool)
        if resolution_bool:
            feedback_msg = msg_dict.get(p)
    return feedback_msg


""" A2 Part B
 
    solveEquation is a function that converts a string representation of an equation to a first-order logic representation, and then
    uses a forward planning algorithm to solve the equation. 
    
    equation:   a String representing the equation to be solved. "x=3", "-3x=6", "3x-2=6", "4+3x=6x-7" are all possible Strings.
                For example, you could call solveEquation('x=6') or solveEquation('-3x=6')
    
    plan:   return a list of Strings, where each String is a step in the plan. The Strings should reference the core actions described in the
            Task Domain part of the assignment description.
    
"""
SAMPLE_EQUATION = '3x-2=6'
SAMPLE_ACTION_PLAN = ['add 2', 'combine RHS constant terms', 'divide 3']


def solveEquation(equation):
    plan = SAMPLE_ACTION_PLAN
    return plan


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
EQUATION = '3x+2=8'
SAMPLE_MISSING_SKILLS = ['S4', 'S5']


def predictSuccess(current_skills, equation):
    missing_skills = SAMPLE_MISSING_SKILLS
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
CURRENT_SKILLS = ['S8', 'S9']
EQUATION = '3x+2=8'
ACTION = 'add -2'
UPDATED_SKILLS = ['S8', 'S9', 'S4']


def stepThroughProblem(equation, action, current_skills):
    feedback_message = M1
    updated_skills = UPDATED_SKILLS
    return [feedback_message, updated_skills]


if __name__ == '__main__':
    print(giveFeedback("CorrectAnswer"))

