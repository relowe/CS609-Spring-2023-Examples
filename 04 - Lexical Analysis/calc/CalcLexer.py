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

    def __next_char():
        # reset line counters
        if self.__cur == "\n":
            self.__line += 1
            self.__col = 0

        # scan a character and keep track of the column
        self.__cur = self.__file.read(1)
        if self.__cur:
            self.__col += 1
