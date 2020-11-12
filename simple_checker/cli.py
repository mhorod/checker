"""
Command Line Interface of the checker
"""
import argparse
import sys

import termcolor


def colored(text, color):
    """Returns string with colored text depending on platform"""
    colored_text = text
    if 'win' not in sys.platform:
        # termcolor works only on linux
        colored_text = termcolor.colored(text, color)
    return colored_text


def print_error(message):
    """Prints message red colored"""
    print(colored(message, "red"))


def print_success(message):
    """Prints message green colored"""
    print(colored(message, "green"))


def get_parsed_args():
    """Parses arguments from stdin"""
    parser = argparse.ArgumentParser(description='Simple test runner')
    parser.add_argument(
        '-p',
        metavar='program',
        default='./main' if 'win' not in sys.platform else 'main',
        help='path to the tested program')

    parser.add_argument('-d',
                        metavar='directory',
                        default='tests',
                        help='path to directory containing tests')

    parser.add_argument('-g',
                        metavar='groups',
                        nargs='+',
                        help="groups in given directory that should be tested")

    parser.add_argument('-v',
                        metavar='verifier',
                        help="path to custom verifier")

    parser.add_argument('-b',
                        metavar='break',
                        default='true',
                        choices=['true', 'false'],
                        help='break on failed tests [true/false]')

    parser.add_argument('-t',
                        metavar='timeout',
                        default=None,
                        type=float,
                        help='time limit after which TLE is raised')

    parser.add_argument(
        '--timer',
        help="run program will have a line 'Time: [float]' on stderr",
        action='store_true')
    parser.add_argument('--sha',
                        help='calculate sha-256 instead of veryfying',
                        action='store_true')

    return parser.parse_args()
