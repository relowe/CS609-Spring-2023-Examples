import CalcLexer
from CalcLexer import Token
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

aryness = {
    Operator.PROG: math.inf,
    Operator.ADD: 2,
    Operator.SUB: 2,
    Operator.MUL: 2,
    Operator.DIV: 2,
    Operator.POW: 2,
    Operator.NEG: 1,
    Operator.LIT: 0
}

class ParseTree:
    def __init__(self, op=None, token=None, children=[]):
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
        for child in self.children[mid:]:
            child.print(level+1)
        
        # print ourself
        extra=""
        if self.token.token in (Token.FLOATLIT, Token.INTLIT):
            extra = ": " + self.token.lexeme
        print(f"{' '*level}{self.op.name}{extra}")

        # print the left hand side
        for child in self.children[0:mid]:
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
            result.add_right(self.__parse_statement())
        
        return result

    def __parse_statement(self):
        """
        < Statement >   ::= < Expression > NEWLINE
        """
        result = self.__parse_expression()
        if not self.__has(Token.NEWLINE):
            self.__must_be(Token.EOF)
        self.__lexer.next()     # when we match a token, we should consume it

        return result

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
        return self.__parse_factor()
        self.__parse_term2()


    def __parse_term2(self):
        """
        < Term' >       ::= TIMES < Factor > < Term' >
                            | DIVIDE < Factor > < Term' >
                            | ""
        """
        if self.__has(Token.TIMES):
            self.__lexer.next()
            self.__parse_factor()
            self.__parse_term2()
        elif self.__has(Token.DIVIDE):
            self.__lexer.next()
            self.__parse_factor()
            self.__parse_term2()

    def __parse_factor(self):
        """
        < Factor >      ::= < Exp > < Factor' >
        """
        return self.__parse_exp()
        self.__parse_factor2()

    def __parse_factor2(self):
        """
        < Factor'>          POW < Factor >
                            | ""
        """
        if self.__has(Token.POW):
            self.__lexer.next()
            self.__parse_factor()
    
    def __parse_exp(self):
        """
        < Exp >         ::= LPAREN  < Expression > RPAREN
                            | MINUS < Exp > 
                            | < Number >

        < Number >      ::= INTLIT
                            | FLOATLIT
        """
        if self.__has(Token.LPAREN):
            self.__lexer.next()
            self.__parse_expression()
            self.__must_be(Token.RPAREN)
            self.__lexer.next()
        elif self.__has(Token.MINUS):
            self.__lexer.next()
            self.__parse_exp()
        elif self.__has(Token.INTLIT):
            result = ParseTree(Operator.LIT, self.__lexer.get_token())
            self.__lexer.next()
            return result
        elif self.__must_be(Token.FLOATLIT):
            self.__lexer.next()



def main():
    """
    A unit test for our lexer.
    """
    if len(sys.argv) == 2:
        file = open(sys.argv[1], 'r')
    else:
        file = sys.stdin
    lexer = CalcLexer.Lexer(file)
    parser = Parser(lexer)
    parser.parse().print()



if __name__ == '__main__':
    main()