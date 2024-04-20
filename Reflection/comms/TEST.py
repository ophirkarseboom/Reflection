from functools import partial

def nice(a, b, c):
    print(a, b, c)


if __name__ == '__main__':
    new_func1 = partial(nice, 1, 2)
    new_func2 = partial(nice, 1, 2, 3)

