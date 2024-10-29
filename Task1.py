import matplotlib.pyplot as plt


class Inequality:
    def __init__(self, x1: float, x2: float, sign: str, result: float) -> None:
        self.x1 = x1
        self.x2 = x2
        if sign not in ['>=', '<=', '=']:
            raise ValueError("The wrong inequality sign is obtained!")
        self.sign = sign
        self.result = result

    def check_the_point(self, x1: float, x2: float) -> bool:
        ...
