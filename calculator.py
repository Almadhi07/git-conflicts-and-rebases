#!/usr/bin/env python3

import sys
import logging
import argparse

from random import seed, randrange

def add():
    return randrange(1000) + randrange(1000)

def subtract():
    return randrange(1000) - randrange(1000)

def setup_cli():
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true',
                        help='Enable extra debugging output')
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
    seed(0)

    logging.info("Welcome to the [not-so] random number calculator!")

    op = randrange(2)
    if op == 0:
        logging.debug("Adding!")
        result = add()
    elif op == 1:
        logging.debug("Subtracting!")
        result = subtract()

    logging.info(f"The result is {result}")

if __name__ == "__main__":
    main()
