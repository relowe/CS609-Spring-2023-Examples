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
    EQUAL = auto()
    ID = auto()
    INPUT = auto()
    INTEGER = auto()
    REAL = auto()
    ARRAY = auto()
    OF = auto()
    WITH = auto()
    BOUNDS = auto()
    LBRACKET = auto()
    RBRACKET = auto()
    COMMA = auto()
    BSEP = auto()
    DOT = auto()
    RECORD = auto()
    END = auto()

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
        self.__in_bsep = False
    

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
        elif self.__lex_kw_or_id():
            pass
        elif self.__lex_bsep_or_dot():
            pass
        else:
            self.__consume()
            self.__set_token(Token.INVALID)

        return self.__token


    def __set_token(self, token, value = None):
        col = self.__col 
        if self.__lexeme:
            col-=len(self.__lexeme)
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
                (')', Token.RPAREN),
                ('=', Token.EQUAL),
                (',', Token.COMMA),
                ('[', Token.LBRACKET),
                (']', Token.RBRACKET))
        
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
        if self.__cur != '.' or self.__start_bsep():
            if self.__lexeme[-1] == '.':
                self.__lexeme = self.__lexeme[0:-1]
            self.__set_token(token, int(self.__lexeme))
            return True
        
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
    
    def __lex_kw_or_id(self):
        """
        Attempt to lex a keyword or an id.
        """

        kw = {'input': Token.INPUT,
              'integer': Token.INTEGER,
              'real': Token.REAL,
              'array': Token.ARRAY,
              'of': Token.OF,
              'with': Token.WITH,
              'bounds' : Token.BOUNDS,
              'record' : Token.RECORD,
              'end' : Token.END }

        # consume characters which match the pattern
        if self.__cur.isalpha() or self.__cur == '_':
            self.__consume()
        else:
            return False
        
        # consume the rest of the consistent characters
        while self.__cur.isalpha() or self.__cur.isdigit() or self.__cur == '_':
            self.__consume()
        
        # create the token
        if self.__lexeme in kw:
            self.__set_token(kw[self.__lexeme])
        else:
            self.__set_token(Token.ID)

        return True
    
    def __lex_bsep_or_dot(self):
        # control the number of periods we need to see
        if self.__in_bsep:
            n = 1
            self.__in_bsep = False
        else:
            n = 2

        for i in range(n):
            if self.__cur != '.':
                if n < 1:
                    return False
                else:
                    self.__set_token(Token.DOT)
                    return True
            self.__consume()
        
        self.__lexeme = '..'
        self.__set_token(Token.BSEP)
        return True
    
    def __start_bsep(self):
        if self.__cur != '.':
            return False
        self.__consume()
        self.__in_bsep = self.__cur == '.'
        return self.__in_bsep
        

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