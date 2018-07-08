import random
from enum import IntEnum, unique
from abc import ABC, abstractmethod


@unique
class CellState(IntEnum):
    EMPTY = 0
    SNAKE_BODY = 1
    FOOD = 2


@unique
class DIRECTION(IntEnum):
    UP = 0
    DOWN = 1
    LEFT = 2
    RIGHT = 3
    STOP = 4


class Snake:
    """
    Represents snake in the game. It contains information about snake body
    and current __direction.
    """
    def __init__(self, board_size, game_state):
        """
        Creates tree blocks as snake body, set current __direction to right
        and updates the game state with snake body positions.
        :param board_size: size of a game board.
        :param game_state: which game state snake updates.
        """
        self.__board_size = board_size
        self.__game_state = game_state
        if self.__board_size <= 5:
            self.__head = [int(self.__board_size/2), int(self.__board_size/2)]
        else:
            self.__head = [int(self.__board_size/4), int(self.__board_size/4)]
        self.__body = [[self.__head[0], self.__head[1]],
                       [self.__head[0]-1, self.__head[1]],
                       [self.__head[0]-2, self.__head[1]]]
        self.__direction = DIRECTION.RIGHT
        for point in self.__body:
            self.__game_state.grid[point[0]][point[1]] = CellState.SNAKE_BODY

    def change_direction(self, direction):
        """
        Change snake __direction.
        :param direction: next snake __direction.
        """
        if direction == DIRECTION.RIGHT and self.__direction != DIRECTION.RIGHT\
                and self.__direction != DIRECTION.LEFT:
            self.__direction = DIRECTION.RIGHT
        elif direction == DIRECTION.LEFT and self.__direction != DIRECTION.LEFT\
                and self.__direction != DIRECTION.RIGHT:
            self.__direction = DIRECTION.LEFT
        elif direction == DIRECTION.UP and self.__direction != DIRECTION.UP\
                and self.__direction != DIRECTION.DOWN:
            self.__direction = DIRECTION.UP
        elif direction == DIRECTION.DOWN and self.__direction != DIRECTION.DOWN\
                and self.__direction != DIRECTION.UP:
            self.__direction = DIRECTION.DOWN

    def move(self, food_position):
        """
        Move the snake to the desired __direction by adding the food to that __direction.
        and remove the tail if the snake does not eat food.
        :param food_position: current position of the food.
        :return: if snake food overlaps current food position.
        """
        if self.__direction == DIRECTION.RIGHT:
            self.__head[0] += 1
        elif self.__direction == DIRECTION.LEFT:
            self.__head[0] -= 1
        elif self.__direction == DIRECTION.UP:
            self.__head[1] -= 1
        elif self.__direction == DIRECTION.DOWN:
            self.__head[1] += 1
        self.__body.insert(0, list(self.__head))
        #  update game state
        try:
            self.__game_state.grid[self.__head[0]][self.__head[1]] = CellState.SNAKE_BODY
        except KeyError:
            pass

        if self.__head == food_position:
            return 1
        else:
            position = self.__body.pop()
            try:
                self.__game_state.grid[position[0]][position[1]] = CellState.EMPTY
            except KeyError:
                pass
            return 0

    def check_collision(self):
        """
        Checks is collision detected.
        :return: is collision detected.
        """
        # Check if the _food collides with the edges of the board
        if self.__head[0] >= self.__board_size or self.__head[0] < 0:
            return True
        elif self.__head[1] >= self.__board_size or self.__head[1] < 0:
            return True
        # Check if the _food collides with the body
        for body in self.__body[1:]:
            if self.__head == body:
                return True
        return False

    @property
    def body(self):
        return self.__body

    @body.setter
    def body(self, value):
        self.__body = value
        self.__head = self.__body[0][:]

    @property
    def head(self):
        return self.__head

    @property
    def direction(self):
        return self.__direction

    @direction.setter
    def direction(self, value):
        self.__direction = value


class FoodSpawn:
    """
    Spawn food in game board. It contains information about
    current food position.
    """
    def __init__(self, board_size, game_state):
        """
        Randomly spawns food position and updates the game state.
        :param board_size: game board size.
        """
        self.__board_size = board_size
        self.__game_state = game_state
        self.__is_food_on_map = False
        self._food = self.spawn_food(game_state.empty_cells())
        self.__game_state.grid[self._food[0]][self._food[1]] = CellState.FOOD

    def spawn_food(self, points):
        """
        Choose random point for next food position.
        :param points: tuples of x,y coordinates.
        :return: randomly chosen point.
        """
        if not self.__is_food_on_map:
            try:
                point = random.sample(points, 1)[0]
                self._food = list(point)
                self.__is_food_on_map = True
                #  update game state
                self.__game_state.grid[self._food[0]][self._food[1]] = CellState.FOOD
            except ValueError:
                return None
        return self._food

    def set_food_on_board(self, bool_value):
        self.__is_food_on_map = bool_value

    @property
    def food(self):
        return self._food

    @food.setter
    def food(self, value):
        self._food = value


class GameState:
    """
    Represents game state. It game state is represented as two
    dimensional dictionary of specific values for snake body and
    food positions
    """
    def __init__(self, height, width, food_spawn=None, snake=None):
        """
        Creates grid, snake and food spawn.
        :param height: height of a game board.
        :param width: wight of a game board.
        """
        self.__height = height
        self.__width = width
        self.__grid = {height: {column: CellState.EMPTY for column in range(self.__width)}
                       for height in range(self.__height)}

        self.__snake = Snake(height, self)
        if snake is not None:
            self.__snake.body = snake
        if food_spawn is None:
            self.__food_spawn = FoodSpawn(self.__height, self)
        else:
            self.__food_spawn = food_spawn

    def empty_cells(self):
        """
        Available position in grid for next food spawn.
        :return: dictionary of indexes in grid.
        """
        return {(i, j) for i in self.__grid.keys() for j in self.__grid[i].keys()
                if [i, j] not in self.__snake.body}

    def print_state(self):
        """
        Prints the current state of a game.
        """
        for i in self.__grid.keys():
            row = ""
            for j in self.__grid[i].keys():
                if self.__grid[i][j] == CellState.EMPTY:
                    row += "-"
                elif self.__grid[i][j] == CellState.SNAKE_BODY:
                    row += "*"
                else:
                    row += "o"
            print(row)
        print("\n\n")

    @property
    def height(self):
        return self.__height

    @height.setter
    def height(self, value):
        self.__height = value

    @property
    def width(self):
        return self.__width

    @width.setter
    def width(self, value):
        self.__width = value

    @property
    def grid(self):
        return self.__grid

    @grid.setter
    def grid(self, value):
        self.__grid = value

    @property
    def snake(self):
        return self.__snake

    @snake.setter
    def snake(self, value):
        self.__snake = value

    @property
    def food_spawn(self):
        return self.__food_spawn

    @food_spawn.setter
    def food_spawn(self, value):
        self.__food_spawn = value


class Problem(ABC):
    """
    Represents game problem that agent needs to solve. It contains
    information about current game state.
    """
    def __init__(self, game_state):
        """
        Creates problem current game state.
        :param game_state: current state of a game.
        """
        self.__game_state = game_state
        self.__snake = self.__game_state.snake
        self.__food = self.__game_state.food_spawn.food

    @abstractmethod
    def get_successors(self, actions):
        """
        Sequence of actions that can be executed in current state
        Actions are represents as triplets: (next_state, action, cost)
        Next_state is represented as tuple of snake body positions.
        In does not store information about food position because food
        position stays the same
        :param actions: previous actions.
        """
        pass

    @abstractmethod
    def is_goal_state(self, state):
        """
        Checks if current state is goal state.
        :param state: current state.
        """
        pass

    def reset(self, game_state, target=None):
        """
        Change current problem to new start state.
        :param target: target position to snake reach
        :param game_state: new start state.
        """
        self.__game_state = game_state
        self.__snake = self.__game_state.snake
        self.__food = self.__game_state.food_spawn.food

    @property
    def snake(self):
        return self.__snake

    @property
    def food(self):
        return self.__food

    @property
    def game_state(self):
        return self.__game_state


class Agent(ABC):
    """
    Represents agent that manipulates with snake actions.
    """

    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def get_next_action(self):
        """
        Returns next action that leads to problem solution.
        """
        pass


class Environment:

    def __init__(self, game_state):
        self.game_state = game_state

    def get_reward(self):
        reward = -1
        if self.game_state.snake.head == self.game_state.food_spawn.food:
            reward = 20
        elif self.game_state.snake.check_collision():
            reward = -20
        return reward

    def get_state(self):
        return tuple(tuple(value for position in self.game_state.snake.body for value in position)), \
               tuple(tuple(position for position in self.game_state.food_spawn.food))
