import random
import datetime
from enum import IntEnum, unique
from model import GameState, DIRECTION
from math import log, sqrt


@unique
class GameStatus(IntEnum):
    WIN = 0
    LOSE = 1
    IN_PROGRESS = 2


class Board:

    def __init__(self, game_state):
        self.__start_state = get_state(game_state)
        # use game state to update snake position
        self.__game_state = GameState(game_state.height, game_state.width)
        self.__game_state.food_spawn.food = game_state.food_spawn.food

    def next_state(self, state, action):
        # copy last state in order to update
        self.__game_state.food_spawn.food = state[1]
        self.__game_state.snake.body = [[state[0][i], state[0][i + 1]]
                                        for i in range(len(state[0])) if i % 2 == 0]
        self.__game_state.snake.direction = action
        # update current state with given action
        self.__game_state.snake.move(self.__game_state.food_spawn.food)
        return get_state(self.__game_state)

    def get_legal_actions(self, state):
        direction = state[-1]
        self.__game_state.snake.change_direction(direction)
        if direction == DIRECTION.UP:
            return [DIRECTION.UP, DIRECTION.LEFT, DIRECTION.RIGHT]
        elif direction == DIRECTION.DOWN:
            return [DIRECTION.DOWN, DIRECTION.LEFT, DIRECTION.RIGHT]
        elif direction == DIRECTION.LEFT:
            return [DIRECTION.LEFT, DIRECTION.DOWN, DIRECTION.UP]
        elif direction == DIRECTION.RIGHT:
            return [DIRECTION.RIGHT, DIRECTION.DOWN, DIRECTION.UP]

    def check_game_status(self, state):
        self.__game_state.snake.body = [[state[0][i], state[0][i + 1]]
                                        for i in range(len(state[0])) if i % 2 == 0]
        if state[0][0] == state[1][0] and state[0][1] == state[1][1]:
            return GameStatus.WIN
        elif self.__game_state.snake.check_collision():
            return GameStatus.LOSE
        else:
            return GameStatus.IN_PROGRESS

    @property
    def start_state(self):
        return self.__start_state

    @start_state.setter
    def start_state(self, value):
        self.__start_state = value


def get_state(game_state):
    return tuple(tuple(value for position in game_state.snake.body for value in position)), \
            tuple(tuple(position for position in game_state.food_spawn.food)), \
            game_state.snake.direction


class MonteCarloTreeSearch:

    def __init__(self, board, **kwargs):
        self.board = board
        self.c = kwargs.get("c", 1.41)
        self.wins = {}
        self.plays = {}
        self.max_depth = 0
        self.states = [board.start_state]
        self.time = datetime.timedelta(milliseconds=kwargs.get("time", 140))
        self.max_moves = kwargs.get("max_moves", 100)

    def get_action(self):
        self.max_depth = 0
        current_state = self.states[-1]
        legal = self.board.get_legal_actions(current_state)

        games = 0
        begin = datetime.datetime.utcnow()
        while datetime.datetime.utcnow() - begin < self.time:
            self.run_simulation()
            games += 1

        states = [self.board.next_state(current_state, p) for p in legal]
        print("Games: {0}, Duration: {1}".format(games, datetime.datetime.utcnow() - begin))

        percent_wins, action = self.choose_action(states)

        # print stats
        for x in sorted(((100 * self.wins.get(s, 0) / self.plays.get(s, 1), self.wins.get(s, 0),
                          self.plays.get(s, 0), s[2]) for s in states), reverse=True):
            print("{3}: {0:.2f}% ({1} / {2})".format(*x))
        print("Maximum max_depth searched:", self.max_depth)

        return action

    def run_simulation(self):
        plays, wins = self.plays, self.wins
        visited = set()
        states_copy = self.states[:]
        state = states_copy[-1]

        expand = True
        status = GameStatus.IN_PROGRESS
        for i in range(1, self.max_moves + 1):
            legal = self.board.get_legal_actions(states_copy[-1])
            states = [self.board.next_state(state, p) for p in legal]

            if all(plays.get(s) for s in states):
                # if we have stats on all of the legal moves, use UCT.
                _, action, state = self.calculate_utc(states)
            else:
                # otherwise, make an random decision.
                state = random.choice(states)

            states_copy.append(state)

            if expand and state not in self.plays:
                expand = False
                self.plays[state] = 0
                self.wins[state] = 0
                if i > self.max_depth:
                    self.max_depth = i

            visited.add(state)
            status = self.board.check_game_status(state)
            if status == GameStatus.WIN or status == GameStatus.LOSE:
                break

        for state in visited:
            if state in plays:
                plays[state] += 1
                self.calculate_reward(state, status)

    def calculate_reward(self, state, status):
        if status == GameStatus.WIN:
            self.wins[state] += 1

    def calculate_utc(self, states):
        plays, wins = self.plays, self.wins
        total_log = log(sum(plays[s] for s in states))
        return max(((wins[s] / plays[s]) + self.c * sqrt(total_log / plays[s]), s[2], s) for s in states)

    def choose_action(self, states):
        """
        Choose next action
        :param states: next available states
        :return: percent wins, action
        """
        # pick the move with the highest percentage of wins.
        return max((self.wins.get(s, 0) / self.plays.get(s, 1), s[2]) for s in states)


class MonteCarloQLearning(MonteCarloTreeSearch):
    """
    Monte Carlo Tree Search algorithm adjusted for Q-learning agent
    """
    def __init__(self, board, **kwargs):
        """
        Initialize all required parameters.
        In this case wins represents cumulative reward.
        :param board: game board
        :param kwargs: parametric arguments
        """
        super().__init__(board, **kwargs)
        self.current_state = self.states[-1]
        self.q_table = kwargs.get("q_table", {})
        self.alpha = kwargs.get("alpha", 0.3)
        self.gamma = kwargs.get("gamma", 0.1)

    def calculate_reward(self, state, status):
        if status == GameStatus.WIN:
            self.wins[state] += 20
        elif status == GameStatus.LOSE:
            self.wins[state] -= 20
        else:
            self.wins[state] -= 1

    def choose_action(self, states):
        state = self.current_state[0], self.current_state[1]
        if state not in self.q_table:
            self.q_table[state] = {ac: 0 for ac in [s[2] for s in states]}

        next_max, next_max_action, next_max_state = self.calculate_utc(states)
        for action, old_q_value in self.q_table[state].items():
            for s in states:
                if s[2] == action:
                    new_q_value = (1 - self.alpha) * old_q_value + self.alpha * \
                                  (self.wins[s] + self.gamma * next_max)
                    self.q_table[state][action] = new_q_value
        return self.wins.get(next_max_state, 0) / self.plays.get(next_max_state, 1), next_max_action
