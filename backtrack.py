#we went with anytree because we saw feasible start as a backtracking problem, and anytree seemed like it would be an effective
#method of constructing a tree to backtrack through, well documented, high functionality, etc.
from anytree import Node, RenderTree
from sympy import symbols, diff
import re

def problem_to_tree(problem):
    """
    Based on this line of code from parabaloid example:
        prob.model.add_subsystem('paraboloid', om.ExecComp('f = (x-3)**2 + x*y + (y+4)**2 - 3'))
    
    We assume 'problem' as it is passed is an OpenMDAO problem, and we constructing the tree from the equation stored in the subsystem


    Level 1 is the initial problem (represented by a function) and the left hand sign of the equation, in this case single variable Y

    1            Y = A*B + C*D
               /   \
              /     \
    2        AB     CD
            /  \    / \
           /    \  /   \
    3     A      B C    D

        Gradients: the gradient list ends up being all leaf nodes at the end of the tree's formation

        Partial Dervivative: Compute the partial derivative of each parent with respect to all it's children
        eg, the PARTIAL of A would be partial_derivative(parent, child) or partial of AB with respect to A, which is B

        All nodes link to both their parent and all children (lead nodes and root nodes only link 1 way)


        per prob.model.add_subsystem('paraboloid', om.ExecComp('f = (x-3)**2 + x*y + (y+4)**2 - 3')),
        subsystem was assumed to be tuple of name and om.ExecComp and that ExecComp was stored as a string
    """
    equation = problem.model.subsystem[1] #abstraction, unsure how to access the equation string stored in subsystem

    equation = equation.split('=')

    lhs = equation[0]
    lhs = lhs.strip(' ')
    root = Node(lhs, gradients=[]) #gradients starts empty, and is filled during back propagation

    rhs = equation[1]
    terms_list = re.split(r'\D', rhs) #rough idea, does not take into account full order of operations

    for each term in terms_list:
        """
        construct an anytree node (as outlined for the root) and 
        store which operation (+, -, /, *, etc.) took you from parent to child

        Example Node AB would be (from level 2 in diagram above):
           node_ab = Node(AB, parent=root, gradients=[], operation='*')

            - AB is the node's name
            - the parent node is the root of the tree in this case
            - gradients are empty until back propagation
            - the operation which forms AB's children is multiplication. Operation of leaf node is null
        """


    return RenderTree(root)
    

def find_feasible_start(problem):
    tree = problem_to_tree(problem)

    equation = problem.model.subsystem[1] #abstraction, unsure how to access the equation string stored in subsystem
    equation = equation.split('=')
    rhs = equation[1]
    exclude = {'*', '/', '+', '-', '0', '1', '2',
               '3', '4', '5', '6', '7', '8', '9'} #characters we don't differentiate with respect to

    symbols = [] #each symbol (eg variable) we want to differentiate with respect to
    for char in rhs:
        if char not in exclude:
            symbols.append(char)

    

    