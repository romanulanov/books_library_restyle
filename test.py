from more_itertools import chunked
iterable = [{0 : 1}, {2 : 3}, {4: 5}, {6: 7}, {8}]
iterable = list(chunked(iterable, 2))
print(iterable)
for i in iterable:
    print(i[0],i[-1])