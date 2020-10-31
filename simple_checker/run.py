import argparse
import configparser
import difflib
import hashlib
import os
import re
import subprocess
import sys
import time

import termcolor
from console_progressbar import ProgressBar

from simple_checker.config import *
from simple_checker.result import *
from simple_checker.cli import *


def run_tests(config):
    print("Testing config:")
    print(config)
    print()

    if not os.path.isdir(config.test_dir):
        print_error(f"No directory `{config.test_dir}`")
        return

    if config.groups is None:
        groups = get_groups_in_dir(config.test_dir)
    else:
        groups = set()
        for pattern in config.groups:
            for group in get_groups_in_dir_matching(config.test_dir, pattern):
                groups.add(group)

    for group in groups:
        group_path = os.path.join(config.test_dir, group)
        run_test_group(group_path, config)


def get_groups_in_dir_matching(test_dir, pattern):
    re_pattern = re.compile(pattern)
    for group in get_groups_in_dir(test_dir):
        if re_pattern.fullmatch(group):
            yield group


def get_groups_in_dir(test_dir):
    for d in os.listdir(test_dir):
        yield d


class InputFromFiles:
    def __init__(self, ins):
        self.ins = ins
        self.next_index = 0

    def has_test(self):
        return self.next_index < len(self.ins)

    def next(self):
        filename = self.ins[self.next_index]
        self.next_index += 1
        return filename

    def test_count(self):
        return len(self.ins)


class OutputFromFiles:
    def __init__(self, outs):
        self.outs = outs
        self.next_index = 0

    def handle_output(self, output_filename):
        status = TestResult.OK
        lines = open(output_filename, "r").readlines()
        correct_lines = open(self.outs[self.next_index], "r").readlines()
        diff = difflib.unified_diff(lines, correct_lines)
        for line in diff:
            if line: status = TestResult.ANS
        self.next_index += 1
        return status

    def summarize(self):
        pass


class OutputChecksum:
    def __init__(self):
        self.checksum = hashlib.sha256()

    def handle_output(self, output_filename):
        buf_size = 1024
        with open(output_filename, 'r') as f:
            while buf := f.read(buf_size):
                buf = "".join(buf.split())
                self.checksum.update(bytes(buf, "ascii"))
        return TestResult.OK

    def summarize(self):
        checksum = self.checksum.hexdigest()[:8]
        print(f"sha-256 checksum: {checksum}")


def run_test_group(group_path, config):
    print(f"Group: {group_path}")
    input_provider = input_provider_from_config(group_path, config)
    output_handler = output_handler_from_config(group_path, config)

    test_count = input_provider.test_count()
    if test_count == 0:
        print_error("Error: empty group")
        return

    progress_bar = ProgressBar(test_count, fill='#')

    group_result = GroupResult()
    for i in range(test_count):
        in_file = input_provider.next()
        target_file = 'tmp.out'
        test_result = run_test(config.program, in_file, 'tmp.out',
                               config.timeout)
        answer_status = output_handler.handle_output(target_file)
        if test_result.status == TestResult.OK:
            test_result.status = answer_status

        group_result.update(test_result)

        if test_result.status != TestResult.OK:
            print(test_result.status)
            message = f"{test_result.status_name} on {in_file}"
            print(termcolor.colored(message, "red"))
            if config.break_on_error:
                break

        progress_bar.print_progress_bar(i + 1)

    print(group_result.summary())
    output_handler.summarize()
    print()


def input_provider_from_config(group_path, config):
    ins = sorted(all_files_with_extension(group_path, '.in'))
    return InputFromFiles(ins)


def output_handler_from_config(group_path, config):
    if config.sha:
        return OutputChecksum()
    else:
        outs = sorted(all_files_with_extension(group_path, '.out'))
        return OutputFromFiles(outs)


def print_error(message):
    print(termcolor.colored(message, "red"))


def print_success(message):
    print(termcolor.colored(message, "green"))


def all_files_with_extension(directory, extension):
    for root, _, files in os.walk(directory):
        for f in files:
            if f.endswith(extension):
                yield os.path.join(root, f)


def run_test(program, in_file, output_target, timeout=None):
    try:
        run_time = time.time()
        subprocess.run(program,
                       stdin=open(in_file, 'r'),
                       stdout=open(output_target, 'w'),
                       check=True,
                       timeout=timeout)
        run_time = time.time() - run_time
    except subprocess.CalledProcessError:
        return TestResult(TestResult.RTE, run_time)
    except subprocess.TimeoutExpired:
        return TestResult(TestResult.TLE, timeout)
    except Exception as e:
        print(e)
    return TestResult(TestResult.OK, run_time)


def config_from_file(filename):
    print("Currently not supported")
    sys.exit(0)
    config = configparser.ConfigParser()
    config.read(filename)
    default = {
        'program': './main',
        'test_dir': 'tests',
        'groups': None,
    }
    if not "TestConfig" in config:
        print_error("Invalid config")
    common_config = config["common"]
    for key in common_config:
        default[key] = common_config

    return TestConfig('', '', '', '', None, None)


def config_from_args(args):

    return TestConfig(args.p, args.d, args.g, args.b == 'true', args.t,
                      args.sha)


def from_cli():
    args = get_parsed_args()
    #if args.c == None:
    config = config_from_args(args)
    #else:
    #    print(f"Loading config from file {args.c}")
    #    print("Input flags will be ignored")
    #    config = config_from_file(args.c)
    run_tests(config)
