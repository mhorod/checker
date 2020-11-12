"""
Core of the checker used to run the tests
"""

import os
import re
import shutil
import subprocess
import time

from console_progressbar import ProgressBar

from simple_checker import cli, config, result, testio


def run_tests(test_config: config.TestConfig) -> None:
    """Run tests with specification given in config"""

    print("Testing config:")
    print(test_config)
    print()

    if not os.path.isdir(test_config.test_dir):
        cli.print_error(f"No directory `{test_config.test_dir}`")
        return

    if test_config.groups is None:
        groups = get_groups_in_dir(test_config.test_dir)
    else:
        groups = set()
        for pattern in test_config.groups:
            for group in get_groups_in_dir_matching(test_config.test_dir,
                                                    pattern):
                groups.add(group)

    for group in groups:
        run_test_group(group, test_config)


def is_final_group(group_dir) -> bool:
    """Checks if group does not contain any directories other than in or out"""
    dirs = os.listdir(group_dir)
    if len(dirs) == 0 or 'in' in dirs:
        return True
    return False


def expand_group(group_dir, pattern):
    """Returns paths of subgroups in group_dir"""
    return get_groups_in_dir_matching(group_dir, pattern)


def get_groups_in_dir_matching(directory, pattern):
    """Returns generator of only those groups in directory that match pattern"""
    re_pattern = re.compile(pattern)
    for group in get_groups_in_dir(directory):
        if re_pattern.fullmatch(group):
            yield os.path.join(directory, group)


def get_groups_in_dir(directory):
    """Return generator of groups in directory"""
    for group in os.listdir(directory):
        yield group


class TestProgress:
    """Keeps track of executed tests"""
    def __init__(self, total):
        self.total = total
        self.current = 0
        self.progress_bar = init_progress_bar(self)

    def update(self, progress) -> None:
        """Increases the counter"""
        self.current = progress
        self.progress_bar.next()

    def display_size(self) -> int:
        """Returns count of characters used to display progress"""
        return 4 + 2 * len(str(self.total))

    def __str__(self):
        return f"{str(self.current).rjust(len(str(self.total)))} / {self.total}"


def init_progress_bar(test_progress):
    """Create progressbar for test_progress"""
    size = shutil.get_terminal_size()
    bar_length = min(80, size.columns - 10 - test_progress.display_size())
    return ProgressBar(test_progress.total,
                       test_progress,
                       fill='#',
                       length=bar_length)


def run_test_group(group_path, test_config):
    """Run tests from given group"""
    print(f"Group: {group_path}")
    if not is_final_group(group_path):
        for group in expand_group(group_path, ".*"):
            run_test_group(group, test_config)
        return

    test_input = test_input_from_config(group_path, test_config)
    test_output = test_output_from_config(group_path, test_config)

    test_count = test_input.test_count()
    if test_count == 0:
        cli.print_error("Error: empty group")
        return

    test_progress = TestProgress(test_count)
    group_result = result.GroupResult()
    for i in range(test_count):
        test_result = run_test(test_config.program, test_input, test_output,
                               test_config.timeout, test_config.timer)
        group_result.update(test_result)

        if test_result.status != result.TestResult.Status.OK:
            message = f"{test_result.status_name} on {test_input.current_name()}"

            cli.print_error(message)
            if test_config.break_on_error:
                break

        test_progress.update(i + 1)

    print(group_result.summary())
    print(test_output.summary())
    print()


def test_input_from_config(group_path, test_config) -> testio.TestInput:  # pylint: disable=W0613
    """Return TestInput object according to the config"""
    ins = sorted(all_files_with_extension(group_path, '.in'))
    return testio.InputFromFiles(ins)


def test_output_from_config(group_path, test_config) -> testio.TestOutput:
    """Return TestOutput object according to the config"""
    handler = None
    if test_config.sha:
        handler = testio.OutputChecksum()
    elif test_config.verifier is not None:
        handler = testio.OutputToVerifier(test_config.verifier)
    else:
        outs = sorted(all_files_with_extension(group_path, '.out'))
        handler = testio.OutputFromFiles(outs)
    return handler


def all_files_with_extension(directory, extension):
    """Return paths to all files with given extension in directory"""
    for root, _, files in os.walk(directory):
        for filename in files:
            if filename.endswith(extension):
                yield os.path.join(root, filename)


def run_test(program,
             test_input: testio.TestInput,
             test_output: testio.TestOutput,
             timeout=None,
             timer=False) -> result.TestResult:
    """Run a single test"""
    status = result.TestResult.Status.OK
    try:
        program_input = test_input.next()
        run_time = time.time()
        run_result = subprocess.run(program,
                                    input=program_input,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    text=True,
                                    check=True,
                                    shell=True,
                                    timeout=timeout)

        run_time = time.time() - run_time
        status = test_output.handle_output(program_input, run_result.stdout)

        if timer:
            stderr = str(run_result.stderr, "ascii")
            for line in stderr.split('\n'):
                if "Time:" in line:
                    run_time = float(line.split(' ')[1])

    except subprocess.CalledProcessError:
        return result.TestResult(result.TestResult.Status.RTE, run_time)
    except subprocess.TimeoutExpired:
        return result.TestResult(result.TestResult.Status.TLE, timeout)
    return result.TestResult(status, run_time)


def config_from_args(args) -> config.TestConfig:
    """Convert args read from cli to config"""
    return config.TestConfig(program=args.p,
                             test_dir=args.d,
                             verifier=args.v,
                             break_on_error=args.b == 'true',
                             groups=args.g or ['.*'],
                             timeout=args.t,
                             timer=args.timer,
                             sha=args.sha)


def from_cli():
    """Run tests with configuration read from cli"""
    args = cli.get_parsed_args()
    test_config = config_from_args(args)
    run_tests(test_config)
