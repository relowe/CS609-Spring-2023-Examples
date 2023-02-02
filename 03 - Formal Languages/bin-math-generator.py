"""
Generate our sample language from the slides.
"""
from random import randint

MAXDEPTH = 10

def s(depth=0):
    """
    s -> e
    """
    return e(depth + 1)


def e(depth=0):
    """
    e -> e + e
    e -> e - e
    e -> e * e
    e -> e / e
    e -> n
    """
    rule = randint(1, 5)
    if rule == 1 and depth <= MAXDEPTH:
        return e(depth + 1) + "+" + e(depth + 1)
    elif rule == 2 and depth <= MAXDEPTH:
        return e(depth + 1) + "-" + e(depth + 1)
    elif rule == 3 and depth <= MAXDEPTH:
        return e(depth + 1) + "*" + e(depth + 1)
    elif rule == 4 and depth <= MAXDEPTH:
        return e(depth + 1) + "/" + e(depth + 1)
    else:
        return n(depth + 1)


def  n(depth=0):
    """
    n -> nd
    n -> d
    """
    rule = randint(1, 2)
    if rule == 1 and depth <= MAXDEPTH:
        return n(depth + 1) + d(depth + 1)
    else:
        return d(depth + 1)

def d(depth=0):
    """
    d -> 0
    d -> 1
    """
    return str(randint(0, 1))


def main():
    # s is the start symbol
    print(s())

if __name__ == '__main__':
    main()