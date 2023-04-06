import CalcLexer
from CalcLexer import Token, TokenDetail
import sys
from enum import Enum, auto
import math

class Operator(Enum):
    PROG = auto()
    ADD = auto()
    SUB = auto()
    MUL = auto()
    DIV = auto()
    POW = auto()
    NEG = auto()
    LIT = auto()
    ASSIGN = auto()
    INPUT = auto()
    VAR = auto()
    ARRAY_VAR = auto()
    DECL = auto()
    ARRAY_DECL = auto()
    BOUNDS = auto()
    REC_DEF = auto()
    REC_DECL = auto()
    REC_ACCESS = auto()

aryness = {
    Operator.PROG: math.inf,
    Operator.ADD: 2,
    Operator.SUB: 2,
    Operator.MUL: 2,
    Operator.DIV: 2,
    Operator.POW: 2,
    Operator.NEG: 1,
    Operator.LIT: 0,
    Operator.ASSIGN: 2,
    Operator.VAR: 0,
    Operator.ARRAY_VAR: 0,
    Operator.INPUT: 1,
    Operator.DECL: 1,
    Operator.ARRAY_DECL: 2,
    Operator.BOUNDS: 0,
    Operator.REC_DEF: 2,
    Operator.REC_DECL: 2,
    Operator.REC_ACCESS: 2,
}

class ParseTree:
    def __init__(self, op=None, token=None, children=None):
        if children == None:
            children = []
        self.op = op
        self.token = token
        self.children = children
    
    def add_left(self, parse_tree):
        """
        Add a left hand child.
        """
        self.children.insert(0, parse_tree)
    
    def add_right(self, parse_tree):
        """
        Add a right hand child.
        """
        self.children.append(parse_tree)
    
    def add_left_leaf(self, parse_tree):
        """
        Add a left leaf to the parse tree.
        """
        # if we are a leaf, absorb the child
        if len(self.children) < aryness[self.op]:
            self.add_left(parse_tree)
            return
        self.children[0].add_left_leaf(parse_tree)

    def add_right_leaf(self, parse_tree):
        """
        Add a left leaf to the parse tree.
        """
        # if we are a leaf, absorb the child
        if len(self.children) < aryness[self.op]:
            self.add_left(parse_tree)
            return
        self.children[-1].add_right_leaf(parse_tree)
    
    def print(self, level=0):
        mid = len(self.children) // 2
        # print the right hand side
        for child in self.children[mid:][::-1]:
            child.print(level+1)
        
        # print ourself
        extra=""
        if self.token and self.token.token in (Token.FLOATLIT, Token.INTLIT):
            extra = ": " + self.token.lexeme
        print(f"{' '*level}{self.op.name}{extra}")

        # print the left hand side
        for child in self.children[0:mid][::-1]:
            child.print(level+1)

class Parser:
    """
    A recursive descent parser for the calc language.
    """
    def __init__(self, lexer):
        self.__lexer = lexer
    
    def parse(self):
        # starts the lexer (puts the first symbol in the look ahead buffer)
        self.__lexer.next()

        # call our start symbol
        return self.__parse_program()




    # Below this line is the private api of the parser
    def __has(self,t):
        """
        Determines if the next token matches token t.
        Returns true if the the current token is t, and false otherwise

        Parameters
            t - A member of CalcLexer.Token
        """
        return self.__lexer.get_token().token == t
    
    def __must_be(self, t):
        """
        Determines if the next token matches token t.
        Returns true if it does, reports an error and aborts the parser 
        otherwise.

        Parameters
            t - A member of CalcLexer.Token
        """
        if self.__has(t):
            return True
        
        sys.stderr.write(f"Unexpected token {self.__lexer.get_token()}\n")
        sys.exit(-1)

    # use the naming convent __parse_nonterm() for all the parser rules
    def __parse_program(self):
        """
        < Program >     ::= < Program > < Statement > 
                            | < Statement >
        """
        result = ParseTree(Operator.PROG)

        while not self.__has(Token.EOF):
            statement = self.__parse_statement()
            if statement:
                result.add_right(statement)
        
        return result


    def __parse_statement(self):
        """
        < Statement >   ::= < Input > NEWLINE
                            | < Var-Decl >
                            | < Ref > < Statement' > NEWLINE
                            | < Record-Decl > NEWLINE
                            | < Expression > NEWLINE
                            | "" NEWLINE
        """
        if self.__has(Token.INPUT):
            result = self.__parse_input()
        elif self.__has(Token.INTEGER) or self.__has(Token.REAL) or self.__has(Token.ARRAY):
            result = self.__parse_var_decl()
        elif self.__has(Token.NEWLINE):
            # null statement
            result = None
        elif self.__has(Token.ID):
            result = self.__parse_ref()
            s2 = self.__parse_statement2()
            if s2:
                s2.add_left_leaf(result)
                result = s2
        elif self.__has(Token.RECORD):
            result = self.__parse_record_decl()
        else:
            result = self.__parse_expression()
        if not self.__has(Token.NEWLINE):
            self.__must_be(Token.EOF)
        self.__lexer.next()     # when we match a token, we should consume it

        return result
    

    def __parse_statement2(self):
        """
        < Statement' >  ::= < Expression'>    
                            | EQUAL < Expression >
                            | ""
        """
        if self.__has(Token.EQUAL):
            # assignment
            tok = self.__lexer.get_token()
            result = ParseTree(Operator.ASSIGN, tok)
            self.__lexer.next()
            result.add_left(self.__parse_expression())
            return result
        else:
            result = self.__parse_term2()
            result2 = self.__parse_expression2()
            if result2:
                if result:
                    result2.add_left_leaf(result)
                result = result2
            return result

    def __parse_input(self):
        """
        < Input > ::= INPUT < Ref >
        """
        self.__must_be(Token.INPUT)
        self.__lexer.next()
        tok = self.__lexer.get_token()
        result = ParseTree(Operator.INPUT, tok)
        result.add_left(self.__parse_ref())
        return result

    
    def __parse_var_decl(self):
        """
        < Var-Decl >    ::= < Simple-Type > ID
                            | < Array-Type > ID

        < Simple-Type > ::= INTEGER | REAL
        """
        if self.__has(Token.INTEGER) or self.__has(Token.REAL):
            # get the token
            tok = self.__lexer.get_token()
            self.__lexer.next()
            
            result = ParseTree(Operator.DECL, tok)
            result.add_left(self.__parse_id())
        elif self.__must_be(Token.ARRAY):
            result = self.__parse_array_decl()
            result.add_right(self.__parse_id())
        return result

    def __parse_array_decl(self):
        """
        < Array-Type >  ::= ARRAY OF < Array-Type > WITH BOUNDS < Array-Bounds > 

        < Array-Type >  ::= < Simple-Type > | RECORD ID 
        """
        self.__must_be(Token.ARRAY)
        self.__lexer.next()
        self.__must_be(Token.OF)
        self.__lexer.next()

        # Temporary way to handle the type specification
        if self.__has(Token.RECORD):
            self.__lexer.next()
        else:
            self.__has(Token.INTEGER) or self.__must_be(Token.REAL)
        typeToken = self.__lexer.get_token()
        self.__lexer.next()

        # check keyword sequence
        self.__must_be(Token.WITH)
        self.__lexer.next()
        self.__must_be(Token.BOUNDS)
        self.__lexer.next()

        # get the bounds
        bounds = self.__parse_array_bounds()

        # assemble the parse tree
        return ParseTree(Operator.ARRAY_DECL, typeToken, [bounds])


    def __parse_array_bounds(self):
        """
        < Array-Bounds > ::= LBRACKET < Bounds-List > RBRACKET

        < Bounds-List >  ::= < Bound > 
                            | < Bounds-List > COMMA < Bound >

        < Bound > ::= INTLIT 
                    | INTLIT BSEP INTLIT
        """
        # opening bracket
        self.__must_be(Token.LBRACKET)
        tok = self.__lexer.get_token()
        self.__lexer.next()

        # build the bounds 
        result = ParseTree(Operator.BOUNDS, tok)

        # bounds list
        done = False
        while not done:
            # get the bounds
            self.__must_be(Token.INTLIT)
            b = self.__lexer.get_token()
            self.__lexer.next()
            if self.__has(Token.BSEP):
                self.__lexer.next()
                self.__must_be(Token.INTLIT)
                ub = self.__lexer.get_token()
                self.__lexer.next()
                lb = b
            else:
                ub = b
                lb = TokenDetail(Token.INTLIT, "1", 1, ub.line, ub.col)

            # add our bounds
            lb = ParseTree(Operator.LIT, lb)
            ub = ParseTree(Operator.LIT, ub)
            result.add_right(lb)
            result.add_right(ub)

            if self.__has(Token.COMMA):
                self.__lexer.next()
            else:
                done = True

        # closing bracket
        self.__must_be(Token.RBRACKET)
        self.__lexer.next()
        return result

    def __parse_record_decl(self):
        """
        < Record-Decl > ::= RECORD ID NEWLINE < Field-List > END
                            | RECORD ID ID
        """
        # get the token and the tag
        self.__must_be(Token.RECORD)
        tok = self.__lexer.get_token()
        self.__lexer.next()
        self.__must_be(Token.ID)
        tag = self.__lexer.get_token()
        self.__lexer.next()

        if self.__has(Token.ID):
            # declaration of a record variable
            self.__must_be(Token.ID)
            id = self.__lexer.get_token()
            self.__lexer.next()
            return self.__build_record_var_decl(tok, tag, id)
        else:
            # record definition
            self.__must_be(Token.NEWLINE)
            self.__lexer.next()
            fields = self.__parse_field_list()
            self.__must_be(Token.END)
            self.__lexer.next()
            result = ParseTree(Operator.REC_DEF, tok)
            result.add_right(ParseTree(Operator.VAR, tag))
            result.add_right(fields)
            return result
    
    def __build_record_var_decl(self, tok, tag, id):
        result = ParseTree(Operator.REC_DECL, tok)
        result.add_right(ParseTree(Operator.VAR, tag))
        result.add_right(ParseTree(Operator.VAR, id))
        return result

    def __parse_field_list(self):
        """
        < Field-List >  ::= < Field-List > < Field-Decl > NEWLINE
                            | < Field-Decl > NEWLINE
        """
        result = ParseTree(Operator.DECL, self.__lexer.get_token())
        while not self.__has(Token.END):
            result.add_right(self.__parse_field_decl())
            self.__must_be(Token.NEWLINE)
            self.__lexer.next()
        
        return result


    def __parse_field_decl(self):
        """
        < Field-Decl >  ::= < Var-Decl >
                         | RECORD ID ID
        """
        if self.__has(Token.RECORD):
            tok = self.__lexer.get_token()
            self.__lexer.next()
            self.__must_be(Token.ID)
            tag = self.__lexer.get_token()
            self.__lexer.next()
            self.__must_be(Token.ID)
            id = self.__lexer.get_token()
            self.__lexer.next()
            return self.__build_record_var_decl(tok, tag, id)
        else:
            return self.__parse_var_decl()

    def __parse_expression(self):
        """
        < Expression >  ::= < Term > < Expression' >
        """
        t = self.__parse_term()
        e2 = self.__parse_expression2()

        # if there is no Expression', return the term
        if e2 == None:
            return t
        
        # if we have an e2, then it is the result and t is its left child
        e2.add_left_leaf(t)
        return e2
        

    def __parse_expression2(self):
        """
        < Expression' > ::= PLUS < Term > < Expression' >
                            | MINUS < Term > < Expression' >
                            | "" <--- this means "no must_be"
        """
        if self.__has(Token.PLUS):
            # capture the token, and build e2
            tok = self.__lexer.get_token()
            e2 = ParseTree(Operator.ADD, tok)
            self.__lexer.next()

            # get the term
            t = self.__parse_term()
            e2.add_right(t)

            # get the e3
            e3 = self.__parse_expression2()
        elif self.__has(Token.MINUS):
            # capture the token, and build e2
            tok = self.__lexer.get_token()
            e2 = ParseTree(Operator.SUB, tok)
            self.__lexer.next()

            # get the term
            t = self.__parse_term()
            e2.add_right(t)

            e3 = self.__parse_expression2() 
        else:
            # the empty case
            return None
        
        if e3 == None:
            return e2
        else:
            e3.add_left_leaf(e2)
            return e3
    

    def __parse_term(self):
        """
        < Term >        ::= < Factor > < Term' >
        """
        f = self.__parse_factor()
        t2 = self.__parse_term2()

        if not t2:
            return f

        t2.add_left_leaf(f)
        return t2


    def __parse_term2(self):
        """
        < Term' >       ::= TIMES < Factor > < Term' >
                            | DIVIDE < Factor > < Term' >
                            | ""
        """
        if self.__has(Token.TIMES):
            t2 = ParseTree(Operator.MUL, self.__lexer.get_token()) 
            self.__lexer.next()
            t2.add_right(self.__parse_factor())
            t3 = self.__parse_term2()
        elif self.__has(Token.DIVIDE):
            t2 = ParseTree(Operator.DIV, self.__lexer.get_token()) 
            self.__lexer.next()
            t2.add_right(self.__parse_factor())
            t3 = self.__parse_term2()
        else:
            # the empty string case
            return None
        
        if not t3:
            return t2 
        t3.add_left_leaf(t2)
        return t3
        

    def __parse_factor(self):
        """
        < Factor >      ::= < Exp > < Factor' >
        """
        ex = self.__parse_exp()
        f2 = self.__parse_factor2()
        if not f2:
            return ex
        f2.add_left_leaf(ex)
        return f2


    def __parse_factor2(self):
        """
        < Factor'>          POW < Factor >
                            | ""
        """
        if self.__has(Token.POW):
            result = ParseTree(Operator.POW, self.__lexer.get_token())
            self.__lexer.next()
            result.add_right(self.__parse_factor())
            return result
        else:
            # empty condition ""
            return None
    
    def __parse_exp(self):
        """
        < Exp >         ::= LPAREN  < Expression > RPAREN
                            | MINUS < Exp > 
                            | < Number >
                            | < Ref >

        < Number >      ::= INTLIT
                            | FLOATLIT
        """
        if self.__has(Token.LPAREN):
            self.__lexer.next()
            result = self.__parse_expression()
            self.__must_be(Token.RPAREN)
            self.__lexer.next()
        elif self.__has(Token.MINUS):
            result = ParseTree(Operator.NEG, self.__lexer.get_token())
            self.__lexer.next()
            result.add_right(self.__parse_exp())
        elif self.__has(Token.ID):
            return self.__parse_ref()
        elif self.__has(Token.INTLIT):
            result = ParseTree(Operator.LIT, self.__lexer.get_token())
            self.__lexer.next()
        elif self.__must_be(Token.FLOATLIT):
            result = ParseTree(Operator.LIT, self.__lexer.get_token())
            self.__lexer.next()
        return result

    def __parse_ref(self):
        """
        < Ref >         ::= ID < Ref' >

        < Ref' >        ::= LBRACKET < Index > RBRACKET < Ref' >
                            | DOT < Ref > 
                            | ""
        """
        self.__must_be(Token.ID)
        tok = self.__lexer.get_token()
        self.__lexer.next()

        if self.__has(Token.LBRACKET):
            self.__lexer.next() # consume the bracket
            result = ParseTree(Operator.ARRAY_VAR, tok, self.__parse_index())
            self.__must_be(Token.RBRACKET)
            self.__lexer.next()
        else:
            result = ParseTree(Operator.VAR, tok)

        if self.__has(Token.DOT):
            # get and consume the dot
            ra = ParseTree(Operator.REC_ACCESS, self.__lexer.get_token())
            self.__lexer.next()

            ra.add_left(result)
            ra.add_right(self.__parse_ref())
            result = ra
        return result


    def __parse_index(self):
        """
        < Index >       ::= < Index > COMMA < Expression >
                            | < Expression >
        NOTE: This does not return a parse tree, it returns a list of 
              expressions.
        """
        # builds the initial result
        e = self.__parse_expression()
        result = [e]

        while self.__has(Token.COMMA):
            self.__lexer.next()
            e = self.__parse_expression()
            result.append(e)

        return result
    
    def __parse_id(self):
        """
        Build a parse tree for an ID
        """
        self.__must_be(Token.ID)
        tok = self.__lexer.get_token()
        self.__lexer.next()
        return ParseTree(Operator.VAR, tok)


def main(file):
    """
    A unit test for our parser.
    """
    lexer = CalcLexer.Lexer(file)
    parser = Parser(lexer)
    parser.parse().print()



if __name__ == '__main__':
    if len(sys.argv) == 2:
        file = open(sys.argv[1], 'r')
    else:
        file = sys.stdin
    main(file)
