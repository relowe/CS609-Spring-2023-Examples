import random
x = 5

if random.choice((True, False)):
    x = 7
    y = 12
    print(f"Inside the block x={x}")
    print(f"Inside the block y={y}")

print(f"Outside the block x={x}")
print(f"Outside the block y={y}")