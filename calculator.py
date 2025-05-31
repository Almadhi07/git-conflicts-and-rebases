#!/usr/bin/env python3

from random import seed, randrange

def add():
    return randrange(1000) + randrange(1000)

def subtract():
    return randrange(1000) - randrange(1000)

def divide():
    return randrange(1000) / randrange(1000)

def multiply():
    return randrange(1000) * randrange(1000)

def main():
    seed(0)

    print("Welcome to the [not-so] random number calculator!")

    op = randrange(4)
    if op == 0:
        print("Adding!")
        result = add()
    elif op == 1:
        print("Subtracting!")
        result = subtract()
    elif op == 2:
        print("Dividing!")
        result = divide()
    elif op == 3:
        print("Multiplying!")
        result = multiply()

    print(f"The result is {result}")

if __name__ == "__main__":
    main()
