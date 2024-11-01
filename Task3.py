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
            if item.value >= 0:
                return True
        return False

    @staticmethod
    def improve(cost_table, plan) -> Plan:
        _plan = plan.__copy__()
        while TransportationProblem.check_plan(cost_table, _plan):
            us, vs = TransportationProblem.calculate_potentials(cost_table, _plan)
            entering_position = TransportationProblem.get_entering_cell_position(
                TransportationProblem.calculate_difference(cost_table, _plan, us, vs)
            ).coordinates
            loop = TransportationProblem.get_loop([cell.coordinates for cell in _plan], [entering_position])
            if not loop:
                exit("Не найден путь цикла!")
            _plan = TransportationProblem.transport(_plan, loop)
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
    def get_loop(plan_positions_,
                 loop_):
        def get_loop(plan_positions, initial_loop):
            stack = [initial_loop]
            visited_loops = set()

            while stack:
                loop = stack.pop()
                entering_cell_position = loop[0]


                if len(loop) > 3:
                    if len(TransportationProblem.get_possible_next_cells(loop, [entering_cell_position])) == 1:
                        return loop
                    else:
                        continue

                not_visited = [coords for coords in plan_positions if coords not in loop]
                possible_next_cells = TransportationProblem.get_possible_next_cells(loop, not_visited)

                for cell in possible_next_cells:
                    new_loop = loop + [cell]
                    new_loop_tuple = tuple(new_loop)

                    if new_loop_tuple not in visited_loops:
                        visited_loops.add(new_loop_tuple)
                        stack.append(new_loop)

            return None

    @staticmethod
    def transport(plan: Plan, loop):
        even_cells = set(loop[0::2])
        odd_cells = set(loop[1::2])

        # Создаем словарь значений для вложения по координатам
        value_map = {cell.coordinates: cell.value for cell in plan}

        # Находим координаты и значение для минимальной четной ячейки
        leaving_coords = sorted(odd_cells, key=lambda coords: value_map[coords])
        leaving_value = value_map[leaving_coords[0]]

        # Создаем новый план, изменяя значения в соответствии с четными и нечетными ячейками
        _plan = Plan([
            Cell(coordinates=cell.coordinates,
                 value=cell.value + leaving_value if cell.coordinates in even_cells else cell.value - leaving_value
                 if cell.coordinates in odd_cells else cell.value)
            for cell in plan
        ])

        return _plan

    @staticmethod
    def forfeit_in_list(_list: list[Cell]) -> int:
        try:
            c_list = _list.copy()
            c_list = [item.value for item in c_list]
            c_list.sort()
            return c_list[1] - c_list[0]
        except Exception as e:
            return -1


cost_table = [[3, 2, 4, 6],
              [2, 3, 1, 2],
              [3, 2, 7, 4]
              ]

supply = [50, 40, 20]

demand = [30, 25, 30, 25]

ct = CostTable.from_int_list(cost_table=cost_table)
tp = TransportationProblem(cost_table=ct, demand=demand, supply=supply)

plan = tp.create_plan(cost_table, supply, demand)
us, vs = tp.calculate_potentials(cost_table, plan)
difference = tp.calculate_difference(cost_table, plan, us, vs)

optimal_plan = tp.improve(cost_table, plan)
print(f"Было : {[str(cell) for cell in plan]}")
print(f"Стало: {[str(cell) for cell in optimal_plan]}")


