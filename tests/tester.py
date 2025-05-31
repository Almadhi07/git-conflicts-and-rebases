#!/usr/bin/env python3

#######################################################################
# IF YOU ARE A STUDENT READING THIS SCRIPT, PLEASE READ THIS COMMENT!
#######################################################################

# Congratulations!  You are looking at the script that runs the tests
# in the GitHub Action for this assignment, and determines whether you
# get a green check or a red X on the pull request.
#
# YOU CANNOT MODIFY THIS FILE, OR ANY OF THE TEXT FILES IN THIS
# REPOSITORY.  The grading script for this assignment will be checking
# all the files in the tests/ folder to make sure that they are
# unaltered.
#
# That being said, the whole point of this script is to ensure that
# you are getting the right answer.  If you find yourself thinking
# that you need to modify this script, then -- by definition -- you
# don't have the right answer.  Reconsider your actions.  :-)
#
# And *that* being said: please feel free to read this script!  But
# you must understand what it is and hw it is used.
#
# This script is a custom testing script, specifically for this
# individual assignment (it is *not* a generalized testing script
# suitable for other testing scenarios).  It is run during the GitHub
# Action whenever you create or modify a GitHub Pull Request.  It
# inspects the `calculator.py` script and determines what capabilities
# exist in that script.  From that, it then determines which tests to
# run, and which test output file in this directory to compare
# against.  Meaning: it only tests against one case at a time,
# depending on what capabilities are in the `calculator.py` script.
# Specifically: this script is designed to be able to test
# `calculator.py` throughout all the different locations in the Git
# DAG in this assignment.  Do *not* think that every test case needs
# to be able to pass at any given location in the DAG.  Instead, only
# *one* test case will be expected to pass at any given location in
# the DAG; this script will a) figure out which test case to run, b)
# run the associated test(s), c) compare the output, and then d)
# determine whether the test passed or failed.
#
# This test script should run with any modern-ish Python 3 version
# (e.g., Python 3.8 or later).

import os
import sys
import shutil
import logging
import argparse
import textwrap
import subprocess
import importlib.util

# Check a Python script and see if a specific function is defined.  As
# expected, this will fail if the Python script itself fails to parse
# or evaluate.
def check_for_function(path, function_name):
    logging.info(f"Checking whether function {function_name} is in {path}")

    # Extract the module name from the file path
    parts = os.path.splitext(os.path.basename(path))
    module_name = parts[0]

    # Load the module dynamically
    try:
        spec = importlib.util.spec_from_file_location(module_name, path)
        if spec is None:
            return False

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

    except Exception as e:
        # If we get an exception, it's likely that the script itself
        # didn't parse (e.g., it had a syntax error).
        logging.error(f"Error loading {path}: {e}")
        return False

    # Check if the function exists in the module
    found = hasattr(module, function_name)
    logging.info(f"--> {found}")
    return found

#----------------

# Minor optimization: only read a given file once
_file_string_cache = dict()

# Look for a specific string in a file
def check_for_string(path, string):
    logging.info(f"Checking whether string \"{string}\" is in {path}")

    if path in _file_string_cache:
        content = _file_string_cache[path]
    else:
        with open(path) as fp:
            content = fp.read()
        _file_string_cache[path] = content

    found = string in content
    logging.info(f"--> {found}")
    return found

#----------------

# Sentinel value
ITERATION = '{i}'

# Run a command and see if it emits the expected output
def check_run(python, expected_results_file, count=1, args=[]):
    outputs = list()
    for i in range(count):
        cmd = [python, './calculator.py']
        for arg in args:
            if arg == ITERATION:
                cmd.append('--seed')
                cmd.append(str(i+1))
            else:
                cmd.append(arg)

        cmd_pp = ' '.join(cmd)
        logging.info(f"Running test iteration {i+1}: {cmd_pp}")
        rc = subprocess.run(cmd, stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT)

        if rc.returncode != 0:
            logging.error(f"Command returned non-zero exit status (rc.returncode): {cmd_pp}")
            exit(1)

        output = rc.stdout.decode('utf-8')
        if output:
            outputs.append(output.strip())

    actual_output = '\n'.join(outputs).strip()

    with open(expected_results_file) as fp:
        expected_output = fp.read().strip()
    if expected_output != actual_output:
        logging.error(f"Command returned unexpected output: {cmd_pp}")
        logging.error("Expected ouput\n" +
                      textwrap.indent(expected_output, "    "))
        logging.error(f"Actual output:\n" +
                      textwrap.indent(actual_output, "    "))
        logging.error("Test failure")
        exit(1)

#----------------

def main():
    logging.basicConfig(level=logging.INFO,
                        stream=sys.stdout,
                        format='%(levelname)s: %(message)s')

    parser = argparse.ArgumentParser()
    parser.add_argument('--force', type=int)
    args = parser.parse_args()

    # Check what functionality the calculator has
    source = "calculator.py"

    logging.info(f"Checking for what capabilities exist in {source}")
    logging.info("NOTE: A \"False\" output here does not mean a test failure!")
    logging.info(f"NOTE: It just means that that capability is not in {source}, which -- at that point in the DAG -- may well be correct!")

    have_original = \
        check_for_function(source, "add") and \
        check_for_function(source, "subtract") and \
        check_for_function(source, "main")

    have_divmul = \
        check_for_function(source, "divide") and \
        check_for_function(source, "multiply")

    have_addsub = \
        check_for_string(source, "Adding then subtracting!") and \
        check_for_string(source, "Subtracting then adding!")

    have_logging = \
        check_for_string(source, "import logging") and \
        check_for_string(source, "logging.basicConfig")

    have_debug = \
        check_for_string(source, "import argparse") and \
        check_for_string(source, "--debug")

    have_seed = \
        check_for_string(source, "import argparse") and \
        check_for_string(source, "--seed")

    # Convert the above booleans into an aggregated value for
    # simplicity of checking, below.
    case = \
         int(have_original) * 1  + \
         int(have_divmul)   * 2  + \
         int(have_addsub)   * 4  + \
         int(have_logging)  * 8  + \
         int(have_debug)    * 16 + \
         int(have_seed)     * 32

    # The command line can override what case we want to run
    if args.force:
        case = args.force

    logging.info(f"Testing case: {case}")

    #----------------

    # Windows installs of Python may not have a "python3" executable.
    python = shutil.which('python3')
    if python is None:
        python = shutil.which('python')
    if python is None:
        logging.error("Cannot find a python3 or python executable -- giving up")

    #----------------

    # Decide how to run the calculator and which output to text against,
    # based on what we found above.
    #
    # Over the course of this assignment, there are finite
    # possibilities that we care about (i.e., need to be able to check
    # for correctness).

    def _run_multiple(base, seed):
        check_run(python, f'{base}.txt')
        check_run(python, f'{base}-debug.txt', args=['--debug'])
        if seed:
            check_run(python, f'{base}-seeds.txt',  args=['--debug', ITERATION],
                      count=100)

    source_dir = os.path.dirname(sys.argv[0])
    base = f'{source_dir}/expected-results'
    if case == 1:
        check_run(python, f'{base}-1-original.txt')

    elif case == 3:
        check_run(python, f'{base}-3-divmul.txt')

    elif case == 5:
        check_run(python, f'{base}-5-addsub.txt')

    elif case == 9:
        check_run(python, f'{base}-9-logging.txt')

    elif case == 25:
        base += '-25-logging'
        _run_multiple(base, seed=False)

    elif case == 57:
        base += '-57-seed'
        _run_multiple(base, seed=True)

    elif case == 59:
        base += '-59-divmul'
        _run_multiple(base, seed=True)

    elif case == 61:
        base += '-61-addsub'
        _run_multiple(base, seed=True)

    elif case == 63:
        base += '-63-all'
        _run_multiple(base, seed=True)

    else:
        # If we got here, the calculator is either non-functional
        # (e.g., syntax error) or it does not have one of the valid
        # sets of functionality that we know how to test.
        logging.error("Did not find a valid testing scenario -- fail")
        exit(1)

    # If we got here, everything passed.  Yay!
    logging.info("SUCCESS!")

main()
