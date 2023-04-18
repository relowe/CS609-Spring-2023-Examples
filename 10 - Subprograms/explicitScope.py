
def f():
    global x # <<---- an explicit scope
    global y
    global f # <<----- Dangerous

    print(f"1.) inside f x={x}")
    x = -x
    print(f"2.) inside f x={x}")
    y = 9
    f = 7

x = 12
f()
print(f"After f x={x}")
print(f"After f y={y}")
f()
