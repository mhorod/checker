"""
Methods of processing input and output data
"""

import abc
import difflib
import hashlib
import subprocess

from simple_checker import result


class TestInput(abc.ABC):
    """Interface of test input"""
    @abc.abstractmethod
    def next(self) -> str:
        """Return next input"""
        raise NotImplementedError

    @abc.abstractmethod
    def current_name(self) -> str:
        """Return identification of current test"""
        raise NotImplementedError

    @abc.abstractmethod
    def test_count(self) -> int:
        """Return number of tests this input can provide"""
        raise NotImplementedError


class TestOutput(abc.ABC):
    """Interface of test output"""
    @abc.abstractmethod
    def handle_output(self, input_data: str,
                      output_data: str) -> result.TestResult:
        """Handle output..."""
        raise NotImplementedError

    def summary(self) -> str:  #pylint: disable=R0201
        """Return additional info about output"""
        return ""


class InputFromFiles(TestInput):
    """Provides input from given set of files"""
    def __init__(self, ins):
        self.ins = ins
        self.next_index = 0

    def next(self):
        filename = self.ins[self.next_index]
        self.next_index += 1
        return open(filename, "r").read()

    def current_name(self):
        return self.ins[self.next_index - 1]

    def test_count(self):
        return len(self.ins)


def remove_whitespace(string):
    """Remove whitespace from string"""
    return "".join(string.split())


class OutputFromFiles(TestOutput):
    """Compares output with given set of files"""
    def __init__(self, outs):
        self.outs = outs
        self.next_index = 0

    def handle_output(self, input_data, output_data):
        status = result.TestResult.Status.OK
        lines = [remove_whitespace(line) for line in output_data.split('\n')]
        lines = [line for line in lines if line]
        correct_lines = [
            remove_whitespace(line)
            for line in open(self.outs[self.next_index]).readlines()
        ]
        correct_lines = [line for line in correct_lines if line]
        diff = difflib.unified_diff(lines, correct_lines)
        for line in diff:
            if line:
                status = result.TestResult.Status.ANS

        self.next_index += 1
        return status


class OutputChecksum(TestOutput):
    """Calculate checksum of output"""
    def __init__(self):
        self.checksum = hashlib.sha256()

    def handle_output(self, input_data, output_data):
        self.checksum.update(bytes(output_data, "ascii"))
        return result.TestResult.Status.OK

    def summary(self):
        checksum = self.checksum.hexdigest()[:8]
        return f"sha-256 checksum: {checksum}"


class OutputToVerifier(TestOutput):
    """Uses external verifier to check output correctness"""
    def __init__(self, verifier):
        self.verifier = verifier

    def handle_output(self, input_data, output_data) -> result.TestResult:
        program_result = subprocess.run(self.verifier,
                                        input=input_data + output_data,
                                        stdout=subprocess.PIPE,
                                        text=True,
                                        shell=True,
                                        check=True)

        stdout = program_result.stdout.strip()
        status = result.TestResult.Status[stdout]
        return status
