def f():
    return 5

def g():
    return 6

def h():
    def fun():
        return 7
    return fun

def create_counter(by):
    return lambda x : x+by

def test(x):
    y = x + 2
    return lambda : y

f = g
print(f())
a = h()
print(a())

by5 = create_counter(5)
by10 = create_counter(10)
print(by5(0))
print(by10(0))

a= test(5)
print(a())