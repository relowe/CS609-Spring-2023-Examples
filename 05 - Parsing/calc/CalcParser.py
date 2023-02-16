import CalcLexer
from CalcLexer import Token
import sys

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
        while not self.__has(Token.EOF):
            self.__parse_statement()

    def __parse_statement(self):
        """
        < Statement >   ::= < Expression > NEWLINE
        """
        self.__parse_expression()
        if not self.__has(Token.NEWLINE):
            self.__must_be(Token.EOF)
        self.__lexer.next()     # when we match a token, we should consume it

    def __parse_expression(self):
        """
        < Expression >  ::= < Term > < Expression' >
        """
        self.__parse_term()
        self.__parse_expression2()

    def __parse_expression2(self):
        """
        < Expression' > ::= PLUS < Term > < Expression' >
                            | MINUS < Term > < Expression' >
                            | "" <--- this means "no must_be"
        """
        if self.__has(Token.PLUS):
            self.__lexer.next()
            self.__parse_term()
            self.__parse_expression2()
        elif self.__has(Token.MINUS):
            self.__lexer.next()
            self.__parse_term()
            self.__parse_expression2() 
    

    def __parse_term(self):
        """
        < Term >        ::= < Factor > < Term' >
        """
        self.__parse_factor()
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
        self.__parse_exp()
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
            self.__lexer.next()
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
    parser.parse()



if __name__ == '__main__':
    main()