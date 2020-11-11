import argparse
import sys

import termcolor


def colored(text, color):
    if 'win' in sys.platform:
        # termcolor isn't supported on windows
        return text
    else:
        return termcolor.colored(text, color)

def print_error(message):
    print(colored(message, "red"))


def print_success(message):
    print(colored(message, "green"))


def get_parsed_args():
    parser = argparse.ArgumentParser(description='Simple test runner')
    parser.add_argument('-p',
                        metavar='program',
                        default='./main' if not 'win' in sys.platform else 'main',
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
    '''TODO:
    parser.add_argument('-G',
                        metavar='generator',
                        help="path to test generator")

    parser.add_argument('-c',
                        metavar='config',
                        help='path to config file for custom checking')

    '''

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
