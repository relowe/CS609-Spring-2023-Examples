"""
A simple tree walk interpreter for calc.
"""
import sys
from enum import Enum, auto
from CalcLexer import Lexer,Token
from CalcParser import Parser,Operator

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


def eval_input(tree, env):
    try:
        name = tree.children[0].token.lexeme
        var = env.get(name)
        if var == None:
            runtime_error(tree, f"Undefined Variable in input {name}")

        # prompt for the variable and read it in
        x = input(f"{name}=")
        
        if var.ref_type == RefType.INT_VAR:
            var.value = int(x)
        elif var.ref_type==RefType.REAL_VAR:
            var.value  = float(x)
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

    var.value = value


def eval_decl(tree, env):
    # get the type
    if tree.token.token == Token.INTEGER:
        ref_type = RefType.INT_VAR
        init = 0
    elif tree.token.token == Token.REAL:
        ref_type = RefType.REAL_VAR
        init = 0.0

    # get the name
    name = tree.children[0].token.lexeme

    # make sure the name is unique
    if env.get(name) != None:
        runtime_error(tree, f"Redeclaration of variable {name}")

    # insert into our environment
    value = RefEntry(init, ref_type)
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
