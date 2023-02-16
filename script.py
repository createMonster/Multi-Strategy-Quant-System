import random

result = []

while len(result) < 17:
    x, y = random.choices(range(100), k=2)
    if x < y and [x, y] not in result:
        result.append([x, y])

print (result)
    