import argparse


def get_parsed_args():
    parser = argparse.ArgumentParser(description='Simple test runner')
    parser.add_argument('-p',
                        metavar='program',
                        default='./main',
                        help='path to the tested program')
    parser.add_argument('-d',
                        metavar='directory',
                        default='tests',
                        help='path to directory containing tests')
    parser.add_argument('-g',
                        metavar='groups',
                        nargs='+',
                        help="groups in given directory that should be tested")
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

    parser.add_argument('--sha',
                        help='calculate sha-256 instead of veryfying',
                        action='store_true')

    return parser.parse_args()
