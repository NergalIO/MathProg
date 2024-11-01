import matplotlib.pyplot as plt


def find_determinant(matrix) -> float:
    return ((matrix[0][0] * matrix[1][1] * matrix[2][2]) +
            (matrix[0][1] * matrix[1][2] * matrix[2][0]) +
            (matrix[1][0] * matrix[2][1] * matrix[0][2]))


class TargetFunction:
    def __init__(self, a: float, b: float, c: float, result: str) -> None:
        self.a = a
        self.b = b
        self.c = c
        if result not in ['max', 'min', 'max, min', 'min, max']:
            raise ValueError("The wrong target function result is obtained!")
        self.result = result

    def calculate(self, x: float, y: float, z: float) -> float:
        return self.a * x + self.b * y + self.c * z


class Inequality:
    def __init__(self, a: float, b: float, c: float, sign: str, result: float) -> None:
        self.a = a
        self.b = b
        self.c = c

        if sign not in ['>=', '<=', '=']:
            raise ValueError("The wrong inequality sign is obtained!")

        if result < 0:
            self.a = -self.a
            self.b = -self.b
            self.c = -self.c
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

    def intersection_point(self, other: 'Inequality', s_other: 'Inequality') -> tuple[float, float, float]:
        delta = [[self.a, self.b, self.c], [other.a, other.b, other.c], [s_other.a, s_other.b, s_other.c]]
        delta_1 = [[self.result, self.b, self.c], [other.result, other.b, other.c], [s_other.result, s_other.b, s_other.c]]
        delta_2 = [[self.a, self.result, self.c], [other.a, other.result, other.c], [s_other.a, s_other.result, s_other.c]]
        delta_3 = [[self.a, self.b, self.result], [other.a, other.b, other.result], [s_other.a, s_other.b, s_other.result]]

        delta_determinant = find_determinant(delta)

        if delta_determinant == 0:
            raise Exception("Determinant can't be found!")

        x = find_determinant(delta_1) / delta_determinant
        y = find_determinant(delta_2) / delta_determinant
        z = find_determinant(delta_3) / delta_determinant

        return x, y, z

    def check_the_point_by_result(self, x: float, y: float, z: float) -> bool:
        left_side = self.a * x + self.b * y + self.c * z
        match self.sign:
            case ">=":
                if left_side >= self.result:
                    return True
                return False
            case "<=":
                if left_side <= self.result:
                    return True
                return False


class LPP:
    def __init__(self, tf: TargetFunction, ineq: list[Inequality]) -> None:
        self.tf = tf
        self.ineq = ineq

    def check_the_point(self, x: float, y: float, z: float) -> bool:
        for _ineq in self.ineq:
            if not _ineq.check_the_point_by_result(x, y, z):
                return False
        return True

    def find_all_intersection_points(self) -> list[tuple[float, float, float]]:
        points = []
        for _ineq in self.ineq:
            for __ineq in self.ineq:
                for ___ineq in self.ineq:
                    if _ineq == __ineq:
                        continue
                    point = _ineq.intersection_point(__ineq, ___ineq)
                    if point in points:
                        continue
                    points.append(point)
        return points

    def find_correct_intersection_points(self, points: list[tuple[float, float, float]]) \
            -> list[tuple[float, float, float]]:
        _points = []
        for x, y, z in points:
            if not self.check_the_point(x, y, z):
                continue
            _points.append((x, y, z))
        return _points

    def find_result(self) -> tuple[float, tuple[float, float, float]] | None:
        points = self.find_all_intersection_points()
        correct_points = self.find_correct_intersection_points(points)
        values = [self.tf.calculate(*point) for point in correct_points]
        if tf.result == "min":
            return min(values), correct_points[values.index(min(values))]
        elif tf.result == "max":
            return max(values), correct_points[values.index(max(values))]
        return None


tf = TargetFunction(9, 12, 10, "min")
ineq1 = Inequality(1, 3, 4, ">=", 60)
ineq2 = Inequality(2, 4, 2, ">=", 50)
ineq3 = Inequality(1, 4, 3, ">=", 12)

lpp = LPP(tf, [ineq1, ineq2, ineq3])
print(lpp.find_result())
