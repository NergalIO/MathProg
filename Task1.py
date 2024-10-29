import matplotlib.pyplot as plt


def gcd(a: float, b: float) -> float:
    a, b = abs(a), abs(b)
    while a != b:
        if a > b:
            a -= b
        else:
            b -= a
    return a


class TargetFunction:
    def __init__(self, a: float, b: float, result: str) -> None:
        self.a = a
        self.b = b
        if result not in ['max', 'min', 'max, min', 'min, max']:
            raise ValueError("The wrong target function result is obtained!")
        self.result = result

    def calculate(self, x: float, y: float) -> float:
        return self.a * x + self.b * y

class Inequality:
    def __init__(self, a: float, b: float, sign: str, result: float) -> None:
        self.a = a
        self.b = b
        if sign not in ['>=', '<=', '=']:
            raise ValueError("The wrong inequality sign is obtained!")
        if result < 0:
            self.a = -self.a
            self.b = -self.b
            self.result = -result
            match sign:
                case ">=":
                    self.sign = "<="
                case "<=":
                    self.sign = ">="
                case "=":
                    self.sign = "="
        else:
            self.sign = sign
            self.result = result

    def get_value_at_y(self, x: float) -> float:
        return (self.result - (self.a * x)) / self.b

    def check_the_point_at_y_by_result(self, x: float, result: float) -> bool:
        match self.sign:
            case ">=":
                return self.get_value_at_y(x) <= result
            case "<=":
                return self.get_value_at_y(x) >= result
            case "=":
                return self.get_value_at_y(x) == result

    def intersection_point(self, other: 'Inequality') -> (float, float):
        delta   = [[self.a, self.b], [other.a, other.b]]
        delta_1 = [[self.result, self.b], [other.result, other.b]]
        delta_2 = [[self.a, self.result], [other.a, other.result]]

        delta_determinant = (delta[0][0]*delta[1][1]) - (delta[0][1]*delta[1][0])

        if delta_determinant == 0:
            raise Exception("Determinant can't be found!")

        x = (delta_1[0][0]*delta_1[1][1] - delta_1[0][1]*delta_1[1][0]) / delta_determinant
        y = (delta_2[0][0]*delta_2[1][1] - delta_2[0][1]*delta_2[1][0]) / delta_determinant

        return x, y


class LPP:
    def __init__(self, tf: TargetFunction, ineq: list[Inequality]) -> None:
        self.tf = tf
        self.ineq = ineq

    def check_the_point(self, x: float, y: float) -> bool:
        for _ineq in self.ineq:
            if not _ineq.check_the_point_at_y_by_result(x, y):
                return False
        return True

    def find_all_intersection_points(self) -> list[tuple[float, float]]:
        points = []
        for _ineq in self.ineq:
            for __ineq in self.ineq:
                if _ineq == __ineq:
                    continue
                point = _ineq.intersection_point(__ineq)
                if point in points:
                    continue
                points.append(point)
        return points

    def find_correct_intersection_points(self, points: list[tuple[float, float]]) -> list[tuple[float, float]]:
        _points = []
        for x, y in points:
            if not self.check_the_point(x, y):
                continue
            _points.append((x, y))
        return _points

    def find_result(self):
        points = self.find_all_intersection_points()
        correct_points = self.find_correct_intersection_points(points)
        if tf.result == "min":
            return min([self.tf.calculate(*point) for point in correct_points])
        if tf.result == "max":
            return max([self.tf.calculate(*point) for point in correct_points])


tf = TargetFunction(176, 185, "min")
ineq1 = Inequality(-40, 35, ">=", 1450)
ineq2 = Inequality(-20, -21, ">=", -2894)
ineq3 = Inequality(30, -21, ">=", -1644)
ineq4 = Inequality(-30, -7, "<=", -708)

lpp = LPP(tf, [ineq1, ineq2, ineq3, ineq4])
print(lpp.find_result())
