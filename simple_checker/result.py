"""
Data that results from running tests
"""

from dataclasses import dataclass
import enum
import statistics

from simple_checker import cli


@dataclass
class TestResult:
    """Result of a single test"""
    class Status(enum.IntEnum):
        """Status of run program"""
        OK = 0
        ANS = 1
        TLE = 2
        RTE = 3

    status_names = ["OK", "ANS", "TLE", "RTE"]

    def __init__(self, status: Status, time: float):
        self.status = status
        self.time = time

    @property
    def status_name(self) -> str:
        """Returns string name of status"""
        return TestResult.status_names[self.status]


class GroupResult:
    """Result of a whole group"""
    def __init__(self):
        self.times = []
        self.status_count = {status: 0 for status in TestResult.status_names}
        self.test_count = 0

    def update(self, test_result):
        """Add test_result to this groups results"""
        self.times.append(test_result.time)
        self.status_count[test_result.status_name] += 1
        self.test_count += 1

    def summary(self) -> str:
        """Returns string summarizing whole group"""
        message = "\n".join(
            f"{status} : {self.status_count[status]}/{self.test_count}"
            for status in self.status_count)
        color = "green" if self.status_count["OK"] == self.test_count else "red"
        message = cli.colored(message, color)

        return message + '\n' + str(TimeSummary(self.times))


@dataclass
class TimeSummary:
    """Run time statistics"""
    def __init__(self, times):
        mean_time = statistics.fmean(times)
        max_time = max(times)
        if len(times) > 1:
            time_stdev = statistics.stdev(times)
        else:
            time_stdev = 0

        self.mean_time = round(mean_time, 4)
        self.max_time = round(max_time, 4)
        self.time_stdev = round(time_stdev, 4)

    def __str__(self):
        return (f"Mean time: {self.mean_time}s\n" +
                f"Max time: {self.max_time}s\n" +
                f"Standard deviation: {self.time_stdev}s")
