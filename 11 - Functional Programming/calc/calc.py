"""
A simple tree walk interpreter for calc.
"""
import sys
from enum import Enum, auto
from CalcLexer import Lexer,Token
from CalcParser import Parser,Operator
import copy

class CalcFunction:
    def __init__(self, parameters, return_type, body):
        self.parameters = parameters
        self.return_type = return_type
        self.body = body

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
    RECORD_VAR = auto()
    FUNCTION = auto()



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
    
    def is_local(self, sym):
        """
        Return true if sym is local to this nested environment
        """
        return sym in self.__sym


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
    
    def set_local(self, sym, value):
        self.__sym[sym] = value
    
    def print_sym(self):
        print(self.__sym)
        if self.__parent:
            self.__parent.print_sym()


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
    elif tree.op == Operator.REC_DEF:
        return eval_rec_def(tree, env)
    elif tree.op == Operator.REC_DECL:
        return eval_rec_decl(tree, env)
    elif tree.op == Operator.REC_ACCESS:
        return eval_rec_access(tree, env)
    elif tree.op == Operator.IF:
        return eval_if(tree, env)
    elif tree.op == Operator.WHILE:
        return eval_while(tree, env)
    elif tree.op == Operator.FUNDEF:
        return eval_fundef(tree, env)
    elif tree.op == Operator.FUNCALL:
        return eval_funcall(tree, env)

def eval_program(tree, env):
    # semantic behavior for now is we print the result of every statement
    # that returns a result
    result = None
    for child in tree.children:
        value = eval_tree(child, env)
        if value != None:
            result = value
            print(result)
    return result


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
    if tree.children[0].op == Operator.REC_ACCESS:
        # record access
        var_tree, var_env = get_record_env(tree.children[0], env)
    else:
        # variable assignment
        var_tree = tree.children[0]
        var_env = env

    # get the name
    name = var_tree.token.lexeme


    # lookup the variable
    var = var_env.get(name)
    if var == None:
        runtime_error(tree, f"Assignment to undeclared variable {name}")

    value = eval_tree(tree.children[1], env)

    # coerce the value
    if var.ref_type == RefType.INT_VAR:
        value = int(value)
    elif var.ref_type == RefType.REAL_VAR:
        value = float(value)

    assign(var_tree, value, var_env)

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
    declare_name(tree, name, value, env)


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
    declare_name(tree, name, value, env)


def eval_rec_def(tree, env):
    # get the tag and build the record name
    tag = tree.children[0].token.lexeme
    name = f"record {tag}"
    rec_env = ReferenceEnvironment()

    # define our fields
    for decl in tree.children[1].children:
        if decl.op == Operator.REC_DECL:
            eval_rec_decl(decl, rec_env, env)
        else:
            eval_tree(decl, rec_env)

    # add the definition to the environment
    declare_name(tree, name, rec_env, env)    


def eval_rec_decl(tree, env, type_env=None):
    if type_env == None:
        type_env = env
    
    # form the record name
    tag = tree.children[0].token.lexeme
    name = f"record {tag}"

    # retrieve record definition
    rec_def = copy.deepcopy(type_env.get(name))
    if rec_def == None:
        runtime_error(tree, f"Undefined {name}")
    
    # insert into our environment
    value = RefEntry(rec_def, RefType.RECORD_VAR)
    declare_name(tree, tree.children[1].token.lexeme, value, env)

def eval_rec_access(tree, env):
    # get the record itself
    rec_env = eval_tree(tree.children[0], env)    

    return eval_tree(tree.children[1], rec_env)

def eval_if(tree, env):
    condition = tree.children[0]
    body = tree.children[1]

    if eval_tree(condition, env) != 0:
        eval_tree(body, env)

def eval_while(tree, env):
    condition = tree.children[0]
    body = tree.children[1]

    while eval_tree(condition, env) != 0:
        eval_tree(body, env)


def eval_fundef(tree, env):
    # get the name
    name = tree.children[0].token.lexeme

    # get the parameters
    params = tree.children[1].children

    # get the return type
    tok = tree.children[2].token.token
    if tok == Token.INTEGER:
        return_type = RefType.INT_VAR
    elif tok == Token.REAL:
        return_type = RefType.REAL_VAR
    else:
        return_type = None
    
    # get the body
    body = tree.children[3]

    # build the function object
    f = CalcFunction(params, return_type, body)
    value = RefEntry(f, RefType.FUNCTION)
    declare_name(tree, name, value, env)


def eval_funcall(tree, env):
    # get the name of the function
    name = tree.children[0].token.lexeme

    # retrieve the function
    entry = env.get(name)
    if entry == None or entry.ref_type != RefType.FUNCTION:
        runtime_error(tree, f"{name} is not a function.")
    fun = entry.value
    
    # verify the number of arguments
    arg_expressions = tree.children[1].children
    if len(arg_expressions) != len(fun.parameters):
        runtime_error(tree, f"Incorrect number of arguments to {name}")
    
    # create the local environment and bind the arguments
    local = ReferenceEnvironment(env)
    for i in range(len(fun.parameters)):
        p = fun.parameters[i]
        if p.op == Operator.DECL:
            # this is by copy of evaluation (pass by value)
            eval_decl(p, local)
            value = eval_tree(arg_expressions[i], env)
            assign_var(p.children[0], value, local)
        else:
            # pass by preference
            name = p.children[1].token.lexeme
            value = env.get(arg_expressions[i])
            if value == None:
                runtime_error(tree, f"Error binding {name}")
            declare_name(tree, name, value)
 
    # run the function on the local environment
    result = eval_tree(fun.body, local)
    if fun.return_type == RefType.INT_VAR:
        result = int(result)
    else:
        result = float(result)
    return result




################ Helper Functions ########################
def get_record_env(tree, env):
    """
    Find the environment of the final record
    Return
        tree, rec_env where tree is the field being accessed
    """
    rec_env = eval_tree(tree.children[0], env)
    field_tree = tree.children[1]
    if field_tree.op == Operator.REC_ACCESS:
        field_tree, rec_env = get_record_env(field_tree, rec_env)
    return field_tree, rec_env

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

def declare_name(tree, name, value, env):
    # make sure the name is unique
    if env.is_local(name):
        runtime_error(tree, f"Redeclaration of variable {name}")
    env.set_local(name, value)


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
