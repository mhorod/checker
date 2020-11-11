import enum
import statistics

from simple_checker import cli

class TestResult:
    class Status(enum.IntEnum):
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
        return TestResult.status_names[self.status]


class GroupResult:
    def __init__(self):
        self.times = []
        self.status_count = {status: 0 for status in TestResult.status_names}
        self.test_count = 0

    def update(self, test_result):
        self.times.append(test_result.time)
        self.status_count[test_result.status_name] += 1
        self.test_count += 1

    def summary(self):
        message = "\n".join(
            f"{status} : {self.status_count[status]}/{self.test_count}"
            for status in self.status_count)
        color = "green" if self.status_count["OK"] == self.test_count else "red"
        message = cli.colored(message, color)

        return message + '\n' + str(TimeSummary(self.times))


class TimeSummary:
    def __init__(self, times):
        mean_time = statistics.fmean(times)
        max_time = max(times)
        time_stdev = statistics.stdev(times)
        self.mean_time = round(mean_time, 4)
        self.max_time = round(max_time, 4)
        self.time_stdev = round(time_stdev, 4)

    def __str__(self):
        return (f"Mean time: {self.mean_time}s\n" +
                f"Max time: {self.max_time}s\n" +
                f"Standard deviation: {self.time_stdev}s")
