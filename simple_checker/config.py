class TestConfig:
    def __init__(self, program, test_dir, groups, break_on_error, timeout,
                 sha):
        self.program = program
        self.test_dir = test_dir
        self.groups = groups
        self.break_on_error = break_on_error
        self.timeout = timeout
        self.sha = sha

    def group_string(self):
        if self.groups is None:
            result = "all"
        else:
            result = " ".join(self.groups)
        return result

    def timeout_string(self):
        if self.timeout is None:
            return "unset"
        else:
            return f"{self.timeout}s"

    def __str__(self):

        result = (f"program: {self.program}\n" +
                  f"test_dir: {self.test_dir}\n" +
                  f"groups: {self.group_string()}\n" +
                  f"break on error: {str(self.break_on_error)}\n" +
                  f"timeout: {self.timeout_string()}")
        if self.sha:
            result += '\n' + "Calculating SHA-256 instead of veryfying."

        return result
