class Cell:
    def __init__(self, coordinates: tuple[int, int], value: int) -> None:
        self.coordinates = coordinates
        self.value = value

    def __copy__(self) -> 'Cell':
        return Cell(coordinates=self.coordinates, value=self.value)

    def __str__(self) -> str:
        return f"Cell(Coordinates: {self.coordinates}, Value: {self.value})"

    def __eq__(self, other: 'Cell') -> bool:
        return self.value == other.value

    def __le__(self, other: 'Cell') -> bool:
        return self.value <= other.value

    def __ge__(self, other: 'Cell') -> bool:
        return self.value >= other.value

    def __lt__(self, other: 'Cell') -> bool:
        return self.value < other.value

    def __gt__(self, other: 'Cell') -> bool:
        return self.value > other.value

    def __ne__(self, other: 'Cell') -> bool:
        return self.value != other.value


class Plan:
    def __init__(self, data: list[Cell]):
        self.data = data

    def get_cell(self, coordinates: tuple[int, int]) -> 'Cell':
        for cell in self.data:
            if cell.coordinates == coordinates:
                return cell
            if not self.check_cell(coordinates):
                self.data.append(Cell(coordinates, 0))
                return self.data[-1]

    def check_cell(self, coordinates) -> bool:
        for cell in self.data:
            if cell.coordinates == coordinates:
                return True
        return False

    def __copy__(self) -> 'Plan':
        return Plan(data=[cell.__copy__() for cell in self.data])

    def __getitem__(self, item: int) -> Cell:
        return self.data[item]

    def __setitem__(self, key, value) -> None:
        self.data[key] = value

    def __iter__(self):
        for item in self.data:
            yield item

    def __len__(self):
        return len(self.data)


class CostTable:
    def __init__(self, data: list[list[Cell]]) -> None:
        self.data = data

    def calculate_cost(self, plan: Plan) -> int:
        return sum([self.data[cell.coordinates[0]][cell.coordinates[1]].value * cell.value for cell in plan])

    @staticmethod
    def from_int_list(cost_table: list[list[int]]) -> 'CostTable':
        for i, line in enumerate(cost_table):
            for j, value in enumerate(line):
                cost_table[i][j] = Cell((i, j), value)
        return CostTable(cost_table)

    def update(self, cost_table: list[list[int]]) -> None:
        for i, line in enumerate(cost_table):
            for j, value in enumerate(line):
                self.data[i][j] = Cell((i, j), value)

    def to_int_list(self) -> list[list[int]]:
        _list = []
        for line in self.data:
            _line = []
            for cell in line:
                _line.append(cell.value)
            _list.append(_line)
        return _list

    def __getitem__(self, i):
        return self.data[i]

    def __len__(self) -> int:
        return len(self.data)


class TransportationProblem:
    def __init__(self, cost_table: CostTable, supply: list[int], demand: list[int]) -> None:
        self.cost_table = cost_table
        self.supply = supply
        self.demand = demand

    @staticmethod
    def create_plan(cost_table, supply, demand) -> Plan:
        supply = supply.copy()
        demand = demand.copy()

        m, n = len(cost_table), len(cost_table[0])
        r_i, c_i = list(range(m)), list(range(n))

        data = []
        while len(data) < m + n - 1:
            i, j, cost = TransportationProblem.analyze_table(cost_table, r_i, c_i)
            cargo = min(supply[i], demand[j])
            supply[i] -= cargo
            demand[j] -= cargo
            data.append(Cell((i, j), cargo))
            if supply[i] == 0:
                r_i.remove(i)
            elif demand[j] == 0:
                c_i.remove(j)
            else:
                raise Exception("Найдена ошибка в создании плана!")
        return Plan(data)

    @staticmethod
    def calculate_potentials(cost_table, plan: Plan) -> tuple[list, list]:
        us, vs = [None] * len(cost_table), [None] * len(cost_table[0])

        us[plan[0].coordinates[0]] = 0
        plan = plan.data.copy()
        while len(plan) > 0:
            for index, cell in enumerate(plan):
                i, j = cell.coordinates
                cost = cost_table[i][j].value
                if us[i] is not None:
                    vs[j] = cost - us[i]
                    plan.pop(index)
                    break
                elif vs[j] is not None:
                    us[i] = cost - vs[j]
                    plan.pop(index)
                    break
        return us, vs

    @staticmethod
    def check_plan(cost_table, plan):
        us, vs = TransportationProblem.calculate_potentials(cost_table, plan)
        difference = TransportationProblem.calculate_difference(cost_table, plan, us, vs)

        for item in difference:
            if item.value > 0:
                return True
        return False

    @staticmethod
    def get_score(cost_table, plan) -> tuple[int, tuple[int, int]]:
        us, vs = TransportationProblem.calculate_potentials(cost_table, plan)
        difference = TransportationProblem.calculate_difference(cost_table, plan, us, vs)
        return max([(cell.value, cell.coordinates) for cell in difference])

    @staticmethod
    def improve(cost_table, plan) -> Plan:
        _plan = plan.__copy__()
        score, pos = TransportationProblem.get_score(cost_table, plan)
        while TransportationProblem.check_plan(cost_table, _plan):
            score, pos = TransportationProblem.transport(cost_table, _plan, pos)
        return _plan

    @staticmethod
    def analyze_table(cost_table_: CostTable, r_i, c_i):
        get_col = lambda j, inds: [cost_table_[i][j] for i in inds]
        get_row = lambda i, inds: [cost_table[i][j] for j in inds]

        forfeit_in_col = lambda j: (j, max(TransportationProblem.forfeit_in_list(get_col(j, r_i)), -1))
        forfeit_in_row = lambda i: (i, max(TransportationProblem.forfeit_in_list(get_row(i, c_i)), -1))

        max_forfeit_in_col = max([forfeit_in_col(j) for j in c_i], key=lambda el: el[1])
        max_forfeit_in_row = max([forfeit_in_row(i) for i in r_i], key=lambda el: el[1])

        if max_forfeit_in_row[0] >= max_forfeit_in_col[0]:
            i = max_forfeit_in_row[0]
            row = get_row(i, c_i)
            min_cost = min(row)
            return i, [j for j, cost in enumerate(cost_table[i])
                       if j in c_i and cost == min_cost][0], min_cost
        else:
            j = max_forfeit_in_col[0]
            col = get_col(j, r_i)
            min_cost = min(col)
            return [i for i, cost in enumerate(get_col(j, list(range(len(cost_table)))))
                    if i in r_i and cost == min_cost][0], j, min_cost

    @staticmethod
    def calculate_difference(cost_table, feasible_plan, us, vs) -> list[Cell]:
        # Преобразуем feasible_plan в множество координат для более быстрого поиска
        feasible_coordinates = {(cell.coordinates) for cell in feasible_plan}
        difference = []

        for i, row in enumerate(cost_table):
            for j, cost in enumerate(row):
                # Проверяем, является ли клетка базисной
                if (i, j) not in feasible_coordinates:
                    difference.append(Cell((i, j), us[i] + vs[j] - cost.value))

        return difference

    @staticmethod
    def get_entering_cell_position(difference) -> Cell:
        return max(difference, key=lambda cell: cell.value)

    @staticmethod
    def get_possible_next_cells(loop, not_visited) -> list[tuple[int, int]]:
        last_node = loop[-1]

        cells_in_row = [cell for cell in not_visited if cell[0] == last_node[0]]
        cells_in_col = [cell for cell in not_visited if cell[1] == last_node[1]]

        if len(loop) == 1:
            return cells_in_row + cells_in_col
        else:
            prev_node = loop[-2]
            if prev_node[0] == last_node[0]:
                return cells_in_col
            return cells_in_row

    @staticmethod
    def transport(cost_table, plan_positions, start_position):
        not_visited = set([cell.coordinates for cell in plan_positions])
        for position1 in [cell for cell in not_visited if not_visited - {start_position}
                          if cell[1] == start_position[0]]:
            for position2 in [cell for cell in not_visited if not_visited - {start_position, position1}
                                if cell[1] == position1[0]]:
                for position3 in [cell for cell in not_visited if not_visited - {start_position, position1, position2}
                                    if cell[1] == position2[0]]:
                    if start_position[1] == position3[1]:
                        print([str(cell) for cell in plan_positions])
                        change = min(plan_positions.get_cell((i, j)).value for i, j in [position1, position3])
                        for i, j in [start_position, position2]:
                            plan_positions.get_cell((i, j)).value += change
                        for i, j in [position1, position3]:
                            plan_positions.get_cell((i, j)).value -= change
                        print([str(cell) for cell in plan_positions])
                        return TransportationProblem.get_score(cost_table, plan)

    @staticmethod
    def forfeit_in_list(_list: list[Cell]) -> int:
        try:
            c_list = _list.copy()
            c_list = [item.value for item in c_list]
            c_list.sort()
            return c_list[1] - c_list[0]
        except Exception as e:
            return -1


cost_table = [[20, 8, 7, 9],
              [14, 4, 12, 5],
              [22, 15, 11, 14]
              ]

supply = [250, 300, 200]

demand = [290, 170, 140, 150]

ct = CostTable.from_int_list(cost_table=cost_table)
tp = TransportationProblem(cost_table=ct, demand=demand, supply=supply)

plan = tp.create_plan(cost_table, supply, demand)
us, vs = tp.calculate_potentials(cost_table, plan)
difference = tp.calculate_difference(cost_table, plan, us, vs)

optimal_plan = tp.improve(cost_table, plan)
