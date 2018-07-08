from model import *
import monte_carlo_tree_search as mc


class MCAgent(Agent):

    def __init__(self, game_state):
        self.__game_state = game_state
        self.__monte_carlo = mc.MonteCarloTreeSearch(mc.Board(self.__game_state))

    def update(self):
        pass

    def get_next_action(self):
        self.__monte_carlo = mc.MonteCarloTreeSearch(mc.Board(self.__game_state))
        return self.__monte_carlo.get_action()
