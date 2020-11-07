import abc
import io
import difflib
import hashlib

from simple_checker import result


class TestInput(abc.ABC):
    @abc.abstractmethod
    def next(self) -> io.TextIOWrapper:
        raise NotImplementedError

    @abc.abstractmethod
    def current_name(self) -> str:
        raise NotImplementedError


class TestOutput(abc.ABC):
    @abc.abstractmethod
    def handle_output(self, data: str) -> result.TestResult:
        raise NotImplementedError

    def summary(self) -> str:
        return ""


class InputFromFiles(TestInput):
    def __init__(self, ins):
        self.ins = ins
        self.next_index = 0

    def has_test(self):
        return self.next_index < len(self.ins)

    def next(self):
        filename = self.ins[self.next_index]
        self.next_index += 1
        return open(filename, "r")

    def current_name(self):
        return self.ins[self.next_index - 1]

    def test_count(self):
        return len(self.ins)


def remove_whitespace(string):
    return "".join(string.split())


class OutputFromFiles(TestOutput):
    def __init__(self, outs):
        self.outs = outs
        self.next_index = 0

    def handle_output(self, data):
        status = result.TestResult.Status.OK
        lines = [remove_whitespace(line) for line in data.split('\n')]
        lines = [line for line in lines if line]
        correct_lines = self.read_lines(self.outs[self.next_index])

        diff = difflib.unified_diff(lines, correct_lines)
        for line in diff:
            if line: status = result.TestResult.Status.ANS

        self.next_index += 1
        return status

    def read_lines(self, filename):
        return [
            remove_whitespace(line)
            for line in open(filename, "r").readlines()
        ]

    def summarize(self):
        pass


class OutputChecksum(OutputFromFiles):
    def __init__(self):
        self.checksum = hashlib.sha256()

    def handle_output(self, data):
        self.checksum.update(bytes(data, "ascii"))
        return result.TestResult.Status.OK

    def summarize(self):
        checksum = self.checksum.hexdigest()[:8]
        print(f"sha-256 checksum: {checksum}")
