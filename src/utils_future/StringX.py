from functools import cached_property


class StringX:
    def __init__(self, x):
        self.x = x

    @cached_property
    def int(self):
        return int(self.x.strip().replace(",", ""))
