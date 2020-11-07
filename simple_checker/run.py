import argparse
import configparser
import difflib
import hashlib
import io
import os
import re
import shutil
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
        run_test_group(group, config)


def is_final_group(group_dir):
    dirs = os.listdir(group_dir)
    if len(dirs) == 0 or 'in' in dirs:
        return True
    return False


def expand_group(group_dir, pattern):
    return get_groups_in_dir_matching(group_dir, pattern)


def get_groups_in_dir_matching(directory, pattern):
    re_pattern = re.compile(pattern)
    for group in get_groups_in_dir(directory):
        if re_pattern.fullmatch(group):
            yield os.path.join(directory, group)


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
        return open(filename, "r")

    def test_count(self):
        return len(self.ins)


def remove_whitespace(string):
    return "".join(string.split())


class OutputFromFiles:
    def __init__(self, outs):
        self.outs = outs
        self.next_index = 0
        self.stream = io.TextIOWrapper(io.BytesIO(), line_buffering=True)

    def handle_output(self):
        status = TestResult.OK
        self.stream.seek(0)
        lines = [remove_whitespace(line) for line in self.stream.readlines()]
        self.stream.seek(0)
        self.stream.truncate(0)
        correct_lines = self.read_lines(self.outs[self.next_index])

        diff = difflib.unified_diff(lines, correct_lines)
        for line in diff:
            if line: status = TestResult.ANS

        self.next_index += 1
        return status

    def read_lines(self, filename):
        return [
            remove_whitespace(line)
            for line in open(filename, "r").readlines()
        ]

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


class TestProgress:
    def __init__(self, total):
        self.total = total
        self.current = 0

    def next(self):
        self.current += 1

    def size(self):
        return 4 + 2 * len(str(self.total))

    def __str__(self):
        return f"{str(self.current).rjust(len(str(self.total)))} / {self.total}"


def run_test_group(group_path, config):
    print(f"Group: {group_path}")
    if not is_final_group(group_path):
        for group in expand_group(group_path, ".*"):
            run_test_group(group, config)
        return

    input_provider = input_provider_from_config(group_path, config)
    output_handler = output_handler_from_config(group_path, config)

    test_count = input_provider.test_count()
    if test_count == 0:
        print_error("Error: empty group")
        return

    size = shutil.get_terminal_size()
    test_progress = TestProgress(test_count)
    progress_bar = ProgressBar(test_count,
                               test_progress,
                               fill='#',
                               length=min(
                                   80,
                                   size.columns - 10 - test_progress.size()))

    group_result = GroupResult()
    for i in range(test_count):
        input_stream = input_provider.next()
        output_stream = output_handler.stream

        test_result = run_test(config.program, input_stream, output_stream,
                               config.timeout)

        answer_status = output_handler.handle_output()

        if test_result.status == TestResult.OK:
            test_result.status = answer_status

        group_result.update(test_result)

        if test_result.status != TestResult.OK:
            print(test_result.status)
            message = f"{test_result.status_name} on {in_file}"
            print(termcolor.colored(message, "red"))
            if config.break_on_error:
                break

        test_progress.next()
        progress_bar.next()

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


def run_test(program, input_stream, output_stream, timeout=None):
    try:
        run_time = time.time()
        run_result = subprocess.run(program,
                                    stdin=input_stream,
                                    stdout=subprocess.PIPE,
                                    check=True,
                                    timeout=timeout)

        output_stream.write(str(run_result.stdout, encoding="utf-8"))
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
