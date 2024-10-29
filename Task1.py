import matplotlib.pyplot as plt


class Inequality:
    def __init__(self, a: float, b: float, sign: str, result: float) -> None:
        self.a = a
        self.b = b
        if sign not in ['>=', '<=', '=']:
            raise ValueError("The wrong inequality sign is obtained!")
        self.sign = sign
        self.result = result

    def get_value_at_x(self, y: float) -> float:
        return (self.result - (self.b * y)) / self.a

    def get_value_at_y(self, x: float) -> float:
        return (self.result - (self.a * x)) / self.b

    def check_the_point(self, x: float, y: float) -> str:
        if self.get_value_at_x(y) == x:
            return "equal"
        elif self.get_value_at_x(y) < x:
            return "lower"
        else:
            return "upper"


class