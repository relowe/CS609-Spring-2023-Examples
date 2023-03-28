"""
A simple tree walk interpreter for calc.
"""
import sys
from enum import Enum, auto
from CalcLexer import Lexer,Token
from CalcParser import Parser,Operator
import copy

class CalcArray:
    def __init__(self, bounds, ref_type):
        """
        Construct an array for the calc language.
        bounds - List of tuples (lbound, ubound)
        ref_type - RefType enumeration field
        """
        self.bounds = bounds
        self.ref_type = ref_type
        self.data = None
        for bound in bounds[::-1]:
            n = bound[1] - bound[0] + 1
            if self.data == None:
                self.data = [0] * n
            else:
                self.data = [copy.deepcopy(self.data) for i in range(n)]

    def get_enclosing_list(self, index):
        bsize = len(index)
        ar = self.data

        # get the enclosing list
        for i in range(bsize-1):
            # subtract the lower bound to make this zero based
            j = index[i] - self.bounds[i][0]
            ar = ar[j]
        return ar


    def get(self, index):
        """
        index - a tuple of integers forming the index to the array
        """
        #get the item
        ar = self.get_enclosing_list(index)
        return ar[index[-1] - self.bounds[-1][0]]


    def set(self, index, value):
        """
        index - a tuple of integers forming the index to the array
        """
        #set the item
        ar = self.get_enclosing_list(index)
        ar[index[-1] - self.bounds[-1][0]] = value



class RefType(Enum):
    INT_VAR = auto()
    REAL_VAR = auto()
    ARRAY_VAR = auto()


class RefEntry:
    def __init__(self, value,ref_type):
        self.value = value
        self.ref_type = ref_type

class ReferenceEnvironment:
    """
    Reference Environment for nested scopes and other types of scopes.
    """
    def __init__(self, parent=None):
        # a dictionary for our local symbols
        self.__sym = {}

        # our enclosing environment
        self.__parent = parent
    
    def get(self, sym):
        """
        Return the associated symbol, return None if not found.
        """
        if sym in self.__sym:
            return self.__sym[sym]
        elif self.__parent:
            return self.__parent.get(sym)
        return None
    
    def set(self, sym, value):
        if self.get(sym) == None:
            # new variable
            self.__sym[sym] = value
        elif sym in self.__sym:
            # local variable
            self.__sym[sym] = value
        else:
            # upstream variable
            return self.__parent.set(sym, value)


def eval_tree(tree, env):
    if tree.op == Operator.PROG:
        return eval_program(tree, env)
    elif tree.op == Operator.ADD:
        return eval_add(tree, env)
    elif tree.op == Operator.SUB:
        return eval_sub(tree, env)
    elif tree.op == Operator.MUL:
        return eval_mul(tree, env)
    elif tree.op == Operator.DIV:
        return eval_div(tree, env)
    elif tree.op == Operator.POW:
        return eval_pow(tree, env)
    elif tree.op == Operator.NEG:
        return eval_neg(tree, env)
    elif tree.op == Operator.LIT:
        return eval_lit(tree, env)
    elif tree.op == Operator.VAR:
        return eval_var(tree, env)
    elif tree.op == Operator.ASSIGN:
        return eval_assign(tree, env)
    elif tree.op == Operator.INPUT:
        return eval_input(tree, env)
    elif tree.op == Operator.DECL:
        return eval_decl(tree, env)
    elif tree.op == Operator.ARRAY_DECL:
        return eval_array_decl(tree, env)
    elif tree.op == Operator.ARRAY_VAR:
        return eval_array_var(tree, env)

def eval_program(tree, env):
    # semantic behavior for now is we print the result of every statement
    # that returns a result
    for child in tree.children:
        result = eval_tree(child, env)
        if result != None:
            print(result)


def eval_add(tree, env):
    left = eval_tree(tree.children[0], env)
    right = eval_tree(tree.children[1], env)
    return left + right


def eval_sub(tree, env):
    left = eval_tree(tree.children[0], env)
    right = eval_tree(tree.children[1], env)
    return left - right


def eval_mul(tree, env):
    left = eval_tree(tree.children[0], env)
    right = eval_tree(tree.children[1], env)
    return left * right

def eval_div(tree, env):
    left = eval_tree(tree.children[0], env)
    right = eval_tree(tree.children[1], env)
    return left / right

def eval_pow(tree, env):
    left = eval_tree(tree.children[0], env)
    right = eval_tree(tree.children[1], env)
    return left ** right

def eval_neg(tree, env):
    left = eval_tree(tree.children[0], env)
    return -left

def eval_lit(tree, env):
    return tree.token.value


def eval_var(tree, env):
    val = env.get(tree.token.lexeme)
    if val == None:
        runtime_error(tree, f"Undefined Variable '{tree.token.lexeme}'")
    return val.value

def eval_array_var(tree, env):
    ar = eval_var(tree, env)
    index = get_array_index(tree, env)
    return ar.get(index)


def eval_input(tree, env):
    try:
        name = tree.children[0].token.lexeme
        var = env.get(name)
        if var == None:
            runtime_error(tree, f"Undefined Variable in input {name}")

        # prompt for the variable and read it in
        x = input(f"{name}=")
        
        if var.ref_type == RefType.INT_VAR:
            x = int(x)
        elif var.ref_type==RefType.REAL_VAR:
            x = float(x)
        
        assign(tree.children[0], x, env)
    except:
        runtime_error(tree, "Invalid Input")


def eval_assign(tree, env):
    # get the name
    name = tree.children[0].token.lexeme

    # lookup the variable
    var = env.get(name)
    if var == None:
        runtime_error(tree, f"Assignment to undeclared variable {name}")

    value = eval_tree(tree.children[1], env)

    # coerce the value
    if var.ref_type == RefType.INT_VAR:
        value = int(value)
    elif var.ref_type == RefType.REAL_VAR:
        value = float(value)

    assign(tree.children[0], value, env)

def eval_decl(tree, env):
    # get the type
    if tree.token.token == Token.INTEGER:
        ref_type = RefType.INT_VAR
        init = 0
    elif tree.token.token == Token.REAL:
        ref_type = RefType.REAL_VAR
        init = 0.0

    # get the name and the value
    name = tree.children[0].token.lexeme
    value = RefEntry(init, ref_type)

    # insert into our env
    declare_name(name, value, env)


def eval_array_decl(tree, env):
    # get the array parameters
    ref_type = tree.token.token
    bounds = tree.children[0].children
    name = tree.children[1].token.lexeme

    # convert the bound list
    bound_list = []
    for i in range(0, len(bounds), 2):
        bound_list.append((bounds[i].token.value, bounds[i+1].token.value))
    
    # construct the array
    ar = CalcArray(bound_list, ref_type)

    # attempt to insert the array
    value = RefEntry(ar, RefType.ARRAY_VAR)
    declare_name(name, value, env)


################ Helper Functions ########################
def assign(tree, value, env):
    if tree.op == Operator.VAR:
        assign_var(tree, value, env)
    elif tree.op == Operator.ARRAY_VAR:
        assign_array_var(tree, value, env)
    
def assign_var(tree, value, env):
    env.get(tree.token.lexeme).value = value

def assign_array_var(tree, value, env):
    ar = env.get(tree.token.lexeme).value
    index = get_array_index(tree, env)
    ar.set(index, value)

def get_array_index(tree, env):
    index = []
    for t in tree.children:
        index.append(eval_tree(t, env))
    return index

def declare_name(name, value, env):
    # make sure the name is unique
    if env.get(name) != None:
        runtime_error(tree, f"Redeclaration of variable {name}")
    env.set(name, value)


def runtime_error(tree, msg):
    sys.stderr.write(f"Runtime error at line {tree.token.line} column {tree.token.col}: {msg}\n")
    sys.exit(-2)


def main(file):
    """
    The main function for the interpreter
    """
    lexer = Lexer(file)
    parser = Parser(lexer)
    tree = parser.parse()
    eval_tree(tree, ReferenceEnvironment())


if __name__ == '__main__':
    if len(sys.argv) == 2:
        file = open(sys.argv[1], 'r')
    else:
        file = sys.stdin
    main(file)
