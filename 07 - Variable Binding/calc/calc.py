"""
A simple tree walk interpreter for calc.
"""
import sys
from CalcLexer import Lexer
from CalcParser import Parser,Operator

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

def eval_program(tree, env):
    # semantic behavior for now is we print the result of every statement
    for child in tree.children:
        print(eval_tree(child, env))


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
    return val

def eval_assign(tree, env):
    # For now, insertion is always allowed. (Declared variables would require more) 
    name = tree.children[0].token.lexeme
    value = eval_tree(tree.children[1], env)
    env.set(name, value)


def runtime_error(tree, msg):
    sys.stderr.write(f"Runtime error at line {tree.token.line} column {tree.token.col}: {msg}")
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