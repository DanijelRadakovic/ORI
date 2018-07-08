from model import *
import monte_carlo_tree_search as mc
import operator
import random
import pickle


class ReinforcementAgent(Agent):

    def __init__(self, environment, alpha=0.3, gamma=0.1, epsilon=0.1):
        self.__environment = environment
        self.q_table = {}
        self.reward = 0
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.state = self.__environment.get_state()
        self.current_action = self.__environment.game_state.snake.direction
        self.current_reward = 0.0

    def get_legal_actions(self):
        if self.__environment.game_state.snake.direction == DIRECTION.UP:
            return [DIRECTION.UP, DIRECTION.LEFT, DIRECTION.RIGHT]
        elif self.__environment.game_state.snake.direction == DIRECTION.DOWN:
            return [DIRECTION.DOWN, DIRECTION.LEFT, DIRECTION.RIGHT]
        elif self.__environment.game_state.snake.direction == DIRECTION.LEFT:
            return [DIRECTION.LEFT, DIRECTION.DOWN, DIRECTION.UP]
        elif self.__environment.game_state.snake.direction == DIRECTION.RIGHT:
            return [DIRECTION.RIGHT, DIRECTION.DOWN, DIRECTION.UP]

    @abstractmethod
    def get_next_action(self):
        pass

    @abstractmethod
    def update(self):
        pass

    def reset(self):
        self.reward = 0

    @property
    def environment(self):
        return self.__environment

    @environment.setter
    def environment(self, value):
        self.__environment = value
        self.state = self.__environment.get_state()


class QAgent(ReinforcementAgent):

    def __init__(self, environment):
        super().__init__(environment)
        try:
            with open("files/q_agent_{0}x{0}.pickle".format(environment.game_state.height), "rb") as file:
                self.q_table = pickle.load(file)
        except(FileNotFoundError, FileExistsError):
            self.q_table = {}

    def get_next_action(self):
        self.state = self.environment.get_state()
        legal_actions = self.get_legal_actions()

        if self.state not in self.q_table:
            self.q_table[self.state] = {ac: 0 for ac in legal_actions}

        action = random.choice(legal_actions)

        # exploration vs. exploitation
        if random.random() > self.epsilon:
            if not len(set(self.q_table[self.state].values())) == 1:
                maximum = max(self.q_table[self.state].items(), key=operator.itemgetter(1))[1]
                action = random.choice([action for action, value in self.q_table[self.state].items()
                                        if value == maximum])
        return action

    def update(self):
        legal_actions = self.get_legal_actions()
        next_state = self.environment.get_state()

        # check if next_state already has q values
        if next_state not in self.q_table:
            self.q_table[next_state] = {ac: 0 for ac in legal_actions}

        old_q_value = self.q_table[self.state][self.current_action]

        # maximum q value for next state actions
        next_max = max(self.q_table[next_state].values())

        new_q_value = (1 - self.alpha) * old_q_value + self.alpha * \
                      (self.current_reward + self.gamma * next_max)
        self.q_table[self.state][self.current_action] = new_q_value


class MCQAgent(QAgent):

    def __init__(self, environment, **kwargs):
        super().__init__(environment)
        try:
            with open("q_agent_table.pickle", "rb") as file:
                self.q_table = pickle.load(file)
        except(FileNotFoundError, FileExistsError):
            self.q_table = {}
        self.__trials_count = kwargs.get("trials", None)
        self.__trials = {}
        self.__monte_carlo = mc.MonteCarloQLearning(mc.Board(self.environment.game_state), q_table=self.q_table,)

    def get_next_action(self):
        self.state = self.environment.get_state()
        legal_actions = self.get_legal_actions()

        if self.state not in self.q_table:
            self.q_table[self.state] = {ac: 0 for ac in legal_actions}

        if self.__trials_count is None:  # always run simulation
            self.__monte_carlo = mc.MonteCarloQLearning(mc.Board(self.environment.game_state))
            return self.__monte_carlo.get_action()
        else:
            if self.state not in self.__trials:
                self.__trials[self.state] = self.__trials_count
            if self.__trials[self.state] > 0:
                # run simulation until is explored enough
                self.__monte_carlo = mc.MonteCarloQLearning(mc.Board(self.environment.game_state))
                self.__trials[self.state] -= 1
                return self.__monte_carlo.get_action()
            else:
                # otherwise, follow policy
                print("PRATI POLITIKU!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                if not len(set(self.q_table[self.state].values())) == 1:
                    maximum = max(self.q_table[self.state].items(), key=operator.itemgetter(1))[1]
                    return random.choice([action for action, value in self.q_table[self.state].items()
                                          if value == maximum])
