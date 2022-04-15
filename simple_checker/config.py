"""
Configuration of the checker
"""

from dataclasses import dataclass, field
import sys
import typing


@dataclass
class Windows:
    """Windows specific defaults"""
    main: str = 'main'


@dataclass
class Linux:
    """Linux specific defaults"""
    main: str = './main'


PLATFORM = Linux() if 'win' not in sys.platform else Windows()


class Extensions:
    """List containing possible extensions"""
    def __init__(self, extensions):
        self.extensions = extensions

    def __or__(self, other):
        return Extensions(self.extensions + other.extensions)

    def __iter__(self):
        return self.extensions.__iter__()


@dataclass
class TestConfig:  # pylint: disable=R0902
    """
    Global configuration
    """
    program: str = PLATFORM.main
    test_dir: str = 'tests'
    verifier: str = None
    break_on_error: bool = True
    groups: typing.List = field(default_factory=lambda: ['.*'])
    timer: bool = False
    timeout: float = None
    sha: bool = False
    correct_answer_extensions: Extensions = Extensions(['.ok', '.out'])

    def group_string(self):
        """Return string of groups"""
        return " ".join(self.groups)

    def timeout_string(self):
        """Return formatted timeout"""
        result = "unset"
        if self.timeout is not None:
            result = f"{self.timeout}s"
        return result

    def __str__(self):
        result = (
            f"program: {self.program}\n" + f"test_dir: {self.test_dir}\n" +
            f"groups: {self.group_string()}\n" +
            f"break on error: {str(self.break_on_error)}\n" +
            f"timeout: {self.timeout_string()}\n" +
            f"correct answer extensions: {' '.join(self.correct_answer_extensions)}"
        )

        if self.sha:
            result += '\n' + "Calculating SHA-256 instead of veryfying."

        if self.timer:
            result += '\n' + "Reading execution time from stderr"

        return result
