"""
Lexer for the calc language.
"""
from enum import Enum, auto
from collections import namedtuple
import sys

class Token(Enum):  # a class which inherits enum
    INVALID = auto()
    EOF = auto()
    NEWLINE = auto()
    PLUS = auto()
    MINUS = auto()
    TIMES = auto()
    DIVIDE = auto()
    POW = auto()
    LPAREN = auto()
    RPAREN = auto()
    INTLIT = auto()
    FLOATLIT = auto()

# Store the details of a token
TokenDetail = namedtuple('TokenDetail', ('token', 
                                         'lexeme', 
                                         'value', 
                                         'line', 
                                         'col'))

class Lexer:
    """
    Calc Lexer
    """
    def __init__(self, file=sys.stdin):
        self.__line = 1
        self.__col = 0
        self.__lexeme = ""
        self.__token = None
        self.__file = file
        self.__cur = None
    

    def next(self):
        """
        Scan for the next token, and return the token.
        Returns: TokenDetail
        """

        # advance to the next character if we do not have one
        if not self.__cur:
            self.__next_char()

        # skip spaces and comments
        self.__skip_space()
        self.__skip_comment()
        
        # start a new lexeme
        self.__lexeme = ''

        # detect EOF
        if not self.__cur:
            self.__lexeme = None
            self.__set_token(Token.EOF)
        elif self.__lex_single():
            pass
        elif self.__lex_number():
            pass
        else:
            self.__consume()
            self.__set_token(Token.INVALID)

        return self.__token


    def __set_token(self, token, value = None):
        col = self.__col - len(self.__lexeme)
        self.__token = TokenDetail(token, self.__lexeme, value, self.__line, col)


    def get_token(self):
        """
        Return the current token
        """
        return self.__token


    def __next_char(self):
        # reset line counters
        if self.__cur == "\n":
            self.__line += 1
            self.__col = 0

        # scan a character and keep track of the column
        self.__cur = self.__file.read(1)
        if self.__cur:
            self.__col += 1

    def __skip_space(self):
        while self.__cur in [' ', '\t']:
            self.__next_char()

    def __skip_comment(self):
        while self.__cur == '#':
            while self.__cur != '\n':
                self.__next_char()
            self.__next_char()
            self.__skip_space()
    
    def __consume(self):
        """
        Add to our lexeme and advance the character stream.
        """
        self.__lexeme += self.__cur
        self.__next_char()

    def __lex_single(self):
        """
        Attempt to match a single character token. Returns true on success
        and false on faliure.

        On success, it sets the token.
        """
        toks = (('\n', Token.NEWLINE),
                ('+', Token.PLUS),
                ('-', Token.MINUS),
                ('*', Token.TIMES),
                ('/', Token.DIVIDE),
                ('^', Token.POW),
                ('(', Token.LPAREN),
                (')', Token.RPAREN))
        
        token = None
        for t in toks:
            if t[0] == self.__cur:
                token = t[1]
                break
        
        # if we do not match, we fail!
        if not token:
            return False
        
        # set the token and return true
        self.__consume()
        self.__set_token(token)
        return True


    def __lex_number(self):
        '''
        Attempt to lex a number, return true on success and false on failure.
        '''
        #try to get the first digit
        if not self.__cur.isdigit():
            return False
        self.__consume()

        # entered the integer state
        token = Token.INTLIT

        # scan all the digits
        while self.__cur.isdigit():
            self.__consume()

        # we found an integer
        if self.__cur != '.':
            self.__set_token(token, int(self.__lexeme))
            return True
        
        # capture the .
        self.__consume()
         
        # enter an invalid state
        token = Token.INVALID
        if not self.__cur.isdigit():
            self.__set_token(token)
            return True
        
        # get the fractional part of the float
        token = Token.FLOATLIT
        while self.__cur.isdigit():
            self.__consume()
        self.__set_token(token, float(self.__lexeme))
        return True
        

def main():
    """
    A unit test for our lexer.
    """
    if len(sys.argv) == 2:
        file = open(sys.argv[1], 'r')
    else:
        file = sys.stdin
    lexer = Lexer(file)

    # run the lexer until we hit the end of the file
    token = lexer.next()
    while token.token != Token.EOF:
        print(token)
        token = lexer.next()
    print(token)


if __name__ == '__main__':
    main()