#!/usr/bin/env python3

import sys
import logging
import argparse

from random import seed, randrange

def add():
    return randrange(1000) + randrange(1000)

def subtract():
    return randrange(1000) - randrange(1000)

def divide():
    return randrange(1000) / randrange(1000)

def multiply():
    return randrange(1000) * randrange(1000)

def setup_cli():
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true',
                        help='Enable extra debugging output')
    parser.add_argument('--seed', default=0,
                        help='Set the random number seed')
    args = parser.parse_args()

    return args

def main():
    args = setup_cli()

    level = logging.INFO
    if args.debug:
        level = logging.DEBUG

    logging.basicConfig(level=level,
                        stream=sys.stdout,
                        format='%(levelname)s: %(message)s')
    seed(args.seed)

    logging.info("Welcome to the [not-so] random number calculator!")

    op = randrange(6)
    if op == 0:
        logging.debug("Adding!")
        result = add()
    elif op == 1:
        logging.debug("Subtracting!")
        result = subtract()
    elif op == 2:
        logging.debug("Dividing!")
        result = divide()
    elif op == 3:
        logging.debug("Multiplying!")
        result = multiply()
    elif op == 4:
        logging.debug("Adding then subtracting!")
        result = add() + subtract()
    elif op == 5:
        logging.debug("Subtracting then adding!")
        result = subtract() - add()

    logging.info(f"The result is {result}")

if __name__ == "__main__":
    main()
