class Settings(object):
    def __init__(
        self,
        min_satisfying_examples=None,
        max_examples=None,
        timeout=None,
    ):
        self.min_satisfying_examples = (
            min_satisfying_examples or default.min_satisfying_examples)
        self.max_examples = max_examples or default.max_examples
        self.timeout = timeout or default.timeout


default = Settings(
    min_satisfying_examples=5,
    max_examples=200,
    timeout=60,
)