from model import *
import util

ACTIONS = [DIRECTION.UP, DIRECTION.DOWN, DIRECTION.RIGHT, DIRECTION.LEFT]


def update_snake_body(snake_body, direction, food_position):
    """
    Move the snake to the desired direction by adding the food to that direction
    and remove the tail if the snake does not eat food.
    :param snake_body: snake body that needs to be updated
    :param direction: snake's direction
    :param food_position: current position of the food.
    :return: updated snake body.
    """
    head = snake_body[0][:]
    new_snake_body = snake_body[:]
    if direction == DIRECTION.RIGHT:
        head[0] += 1
    elif direction == DIRECTION.LEFT:
        head[0] -= 1
    elif direction == DIRECTION.UP:
        head[1] -= 1
    elif direction == DIRECTION.DOWN:
        head[1] += 1

    new_snake_body.insert(0, head)

    if head != food_position:
        new_snake_body.pop()
    return new_snake_body


class EatFoodProblem(Problem):

    def __generate_body(self, actions):
        new_snake = self.snake.body[:]
        for direction in actions:
            head = new_snake[0][:]
            if direction == DIRECTION.RIGHT:
                head[0] += 1
            elif direction == DIRECTION.LEFT:
                head[0] -= 1
            elif direction == DIRECTION.UP:
                head[1] -= 1
            elif direction == DIRECTION.DOWN:
                head[1] += 1
            else:
                continue
            new_snake.insert(0, head)
            new_snake.pop()
        return new_snake

    def get_successors(self, actions):
        successors = []
        snake_body = self.__generate_body(actions)
        for action in ACTIONS:
            new_snake_body = update_snake_body(snake_body, action, self.food)
            cost = 1
            #  if hits a wall set cost to 999
            if not (new_snake_body[0][0] >= self.game_state.width or new_snake_body[0][0] < 0)\
                    and not (new_snake_body[0][1] >= self.game_state.height or new_snake_body[0][1] < 0):
                collision = False
                for body in new_snake_body[1:]:
                    if new_snake_body[0] == body:
                        collision = True
                        break
                if not collision:
                    successors.append((new_snake_body[0], action, cost))
        return successors

    def is_goal_state(self, state):
        return state == self.food


class ReachPositionProblem(Problem):

    def __init__(self, game_state):
        super().__init__(game_state)
        self.__target = [game_state.snake.head[0], 0]
        self.__generate_targets(game_state.width-1)
        self.__index = 0

    def __generate_targets(self, n):
        self.__targets = {0: [0, 0]}
        counter = 1
        side = 0  # 0 for left 1 for right
        for i in range(1, n+1, 1):
            if side == 0:
                if i == n:
                    self.__targets[counter] = [0, i]
                    counter += 1
                    self.__targets[counter] = [n, i]
                    counter += 1
                    self.__targets[counter] = [n, 0]
                    break
                else:
                    self.__targets[counter] = [0, i]
                    counter += 1
                    self.__targets[counter] = [n-1, i]
                    counter += 1
                side = 1
            else:
                self.__targets[counter] = [n-1, i]
                counter += 1
                self.__targets[counter] = [0, i]
                counter += 1
                side = 0

    def __generate_body(self, actions):
        new_snake = self.snake.body[:]
        for direction in actions:
            head = new_snake[0][:]
            if direction == DIRECTION.RIGHT:
                head[0] += 1
            elif direction == DIRECTION.LEFT:
                head[0] -= 1
            elif direction == DIRECTION.UP:
                head[1] -= 1
            elif direction == DIRECTION.DOWN:
                head[1] += 1
            else:
                continue
            new_snake.insert(0, head)
            new_snake.pop()
        return new_snake

    def get_successors(self, actions):
        successors = []
        snake_body = self.__generate_body(actions)
        for action in ACTIONS:
            new_snake_body = update_snake_body(snake_body, action, self.food)
            cost = 1
            #  if hits a wall set cost to 999
            if not (new_snake_body[0][0] >= self.game_state.width or new_snake_body[0][0] < 0) \
                    and not (new_snake_body[0][1] >= self.game_state.height or new_snake_body[0][1] < 0):
                collision = False
                for body in new_snake_body[1:]:
                    if new_snake_body[0] == body:
                        collision = True
                        break
                if not collision:
                    successors.append((new_snake_body[0], action, cost))
        return successors

    def is_goal_state(self, state):
        return state == self.__target

    def reset(self, game_state, target=None):
        super().reset(game_state)
        self.__target = self.__targets[self.__index]
        self.__index = (self.__index + 1) % len(self.__targets)

    @property
    def target(self):
        return self.__target


def create_key(state):
    key = ""
    for point in state:
        key += str(point[0]) + str(point[1])
    return key


def a_star(problem, data_structure):
    visited = {}
    data_structure.push([problem.snake.body[0], [DIRECTION.STOP], 0])
    while not data_structure.is_empty():
        path = data_structure.pop()
        current_state = path[0]

        if problem.is_goal_state(current_state):
            return path[1][1:]

        try:
            if visited[str(current_state[0]) + str(current_state[1])]:
                visited[str(current_state[0]) + str(current_state[1])] = True
        except KeyError:
            visited[str(current_state[0]) + str(current_state[1])] = True
            for successor in problem.get_successors(path[1]):
                try:
                    if visited[str(successor[0][0]) + str(successor[0][1])]:
                        visited[str(successor[0][0]) + str(successor[0][1])] = True
                except KeyError:
                    successor_path = [path[1][:]]  # copy only action for optimisation purpose
                    successor_path.insert(0, successor[0])   # add new snake position
                    successor_path[1].append(successor[1])  # add new action
                    successor_path.insert(2, path[2] + successor[2])   # add new action cost
                    data_structure.push(successor_path)
    return []


def a_star_iterable(problem, data_structure, iterations=1):
    visited = {}
    data_structure.push([problem.snake.body[0], [DIRECTION.STOP], 0])
    i = 0
    while not data_structure.is_empty():
        path = data_structure.pop()
        current_state = path[0]

        if problem.is_goal_state(current_state) or i == iterations:
            return path[1][1:]

        try:
            if visited[str(current_state[0]) + str(current_state[1])]:
                visited[str(current_state[0]) + str(current_state[1])] = True
        except KeyError:
            visited[str(current_state[0]) + str(current_state[1])] = True
            for successor in problem.get_successors(path[1]):
                try:
                    if visited[str(successor[0][0]) + str(successor[0][1])]:
                        visited[str(successor[0][0]) + str(successor[0][1])] = True
                except KeyError:
                    successor_path = [path[1][:]]  # copy only action for optimisation purpose
                    successor_path.insert(0, successor[0])  # add new snake position
                    successor_path[1].append(successor[1])  # add new action
                    successor_path.insert(2, path[2] + successor[2])  # add new action cost
                    data_structure.push(successor_path)
            i = i + 1
    return


class SearchAgent(Agent):
    """
    Represents agent that manipulates with snake actions.
    """
    def __init__(self, problem=None):
        """
        Creates agent with problem that needs to solve.
        :param problem: current problem
        """
        self.__problem = problem

    @abstractmethod
    def update(self):
        pass

    @property
    def problem(self):
        return self.__problem


class RandomSearchAgent(SearchAgent):

    def update(self):
        pass

    def get_next_action(self):
        return random.choice(ACTIONS)


class ZigZagSearchAgent(SearchAgent):

    def __init__(self, problem=None):
        super().__init__(problem)
        self.__data_structure = util.PriorityQueueWithFunction(
            lambda path: path[2] + self.__heuristic(path[0]))
        self.__actions = a_star_iterable(self.problem, self.__data_structure, 1)

    def update(self):
        self.__data_structure.clear()
        self.__actions = a_star_iterable(self.problem, self.__data_structure, 1)

    def get_next_action(self):
        if self.__actions is None:
            return random.choice(ACTIONS)
        elif len(self.__actions) == 0:
            self.__actions = a_star_iterable(self.problem, self.__data_structure, 1)
            if self.__actions is None or len(self.__actions) == 0:
                return random.choice(ACTIONS)
        return self.__actions.pop(0)

    def __heuristic(self, snake_head):
        xy1 = snake_head
        xy2 = self.problem.food
        return ((xy1[0] - xy2[0]) ** 2 + (xy1[1] - xy2[1]) ** 2) ** 0.5


class OroborusSearchAgent(SearchAgent):

    def __init__(self, problem=None):
        super().__init__(problem)
        self.__data_structure = util.PriorityQueueWithFunction(
            lambda path: path[2] + self.__heuristic(path[0]))
        self.__actions = a_star(self.problem, self.__data_structure)

    def __heuristic(self, snake_head):
        xy1 = snake_head
        xy2 = self.problem.target
        return ((xy1[0] - xy2[0]) ** 2 + (xy1[1] - xy2[1]) ** 2) ** 0.5

    def get_next_action(self):
        if len(self.__actions) == 0:
            self.__actions = a_star_iterable(self.problem, self.__data_structure, 10)
            if len(self.__actions) == 0:
                return random.choice(ACTIONS)
        return self.__actions.pop(0)

    def update(self):
        self.__data_structure.clear()
        self.__actions = a_star(self.problem, self.__data_structure)

    def action_count(self):
        return len(self.__actions)


class SmartSearchAgent(SearchAgent):

    def __init__(self, problem=None):
        super().__init__(problem)
        self.__data_structure = util.PriorityQueueWithFunction(
            lambda path: path[2] + self.__heuristic(path[0]))
        self.__remain_alive = False
        self.__actions = a_star(self.problem, self.__data_structure)

    def update(self):
        self.__data_structure.clear()

    def get_next_action(self):
        if len(self.__actions) == 0:
            self.__actions = a_star(self.problem, self.__data_structure)
            if len(self.__actions) == 0:
                try:
                    self.__actions = [self.__stay_alive()[0]]
                except IndexError:
                    return random.choice(ACTIONS)
        return self.__actions.pop(0)

    def __heuristic(self, snake_head):
        xy1 = snake_head
        xy2 = self.problem.food
        return ((xy1[0] - xy2[0]) ** 2 + (xy1[1] - xy2[1]) ** 2) ** 0.5

    def __stay_alive(self):
        problem = self.problem
        visited = {}
        data_structure = util.PriorityQueueWithFunction(lambda x: -len(x[1]))
        results = util.PriorityQueueWithFunction(lambda x: -len(x[1]))
        data_structure.push([problem.snake.body[0], [DIRECTION.STOP], 0])

        while not data_structure.is_empty():
            path = data_structure.pop()
            results.push(path)
            current_state = path[0]

            try:
                if visited[str(current_state[0]) + str(current_state[1])]:
                    visited[str(current_state[0]) + str(current_state[1])] = True
            except KeyError:
                visited[str(current_state[0]) + str(current_state[1])] = True
                for successor in problem.get_successors(path[1]):
                    try:
                        if visited[str(successor[0][0]) + str(successor[0][1])]:
                            visited[str(successor[0][0]) + str(successor[0][1])] = True
                    except KeyError:
                        successor_path = [path[1][:]]  # copy only action for optimisation purpose
                        successor_path.insert(0, successor[0])  # add new snake position
                        successor_path[1].append(successor[1])  # add new action
                        successor_path.insert(2, path[2] + successor[2])  # add new action cost
                        data_structure.push(successor_path)
        return results.pop()[1][1:]
