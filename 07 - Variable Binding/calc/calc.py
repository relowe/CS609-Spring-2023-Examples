"""
A simple tree walk interpreter for calc.
"""
import sys
from CalcLexer import Lexer
from CalcParser import Parser,Operator

def eval_tree(tree):
    if tree.op == Operator.PROG:
        return eval_program(tree)
    elif tree.op == Operator.ADD:
        return eval_add(tree)
    elif tree.op == Operator.SUB:
        return eval_sub(tree)
    elif tree.op == Operator.MUL:
        return eval_mul(tree)
    elif tree.op == Operator.DIV:
        return eval_div(tree)
    elif tree.op == Operator.POW:
        return eval_pow(tree)
    elif tree.op == Operator.NEG:
        return eval_neg(tree)
    elif tree.op == Operator.LIT:
        return eval_lit(tree)

def eval_program(tree):
    # semantic behavior for now is we print the result of every statement
    for child in tree.children:
        print(eval_tree(child))


def eval_add(tree):
    left = eval_tree(tree.children[0])
    right = eval_tree(tree.children[1])
    return left + right


def eval_sub(tree):
    left = eval_tree(tree.children[0])
    right = eval_tree(tree.children[1])
    return left - right


def eval_mul(tree):
    left = eval_tree(tree.children[0])
    right = eval_tree(tree.children[1])
    return left * right

def eval_div(tree):
    left = eval_tree(tree.children[0])
    right = eval_tree(tree.children[1])
    return left / right

def eval_pow(tree):
    left = eval_tree(tree.children[0])
    right = eval_tree(tree.children[1])
    return left ** right

def eval_neg(tree):
    left = eval_tree(tree.children[0])
    return -left

def eval_lit(tree):
    return tree.token.value


def main(file):
    """
    The main function for the interpreter
    """
    lexer = Lexer(file)
    parser = Parser(lexer)
    tree = parser.parse()
    eval_tree(tree)


if __name__ == '__main__':
    if len(sys.argv) == 2:
        file = open(sys.argv[1], 'r')
    else:
        file = sys.stdin
    main(file)