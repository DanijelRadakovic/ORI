import pygame
import sys
from search_agents import *
from reinforcement_agents import *
from general_agents import MCAgent

# Define Constants
HEAD_COLOR = (0, 100, 0)  # Dark Green
BODY_COLOR = (0, 200, 0)  # Light Green
FOOD_COLOR = (200, 0, 0)  # Dark Red


class Game(ABC):

    def __init__(self, board_size, agent=None, game_speed=10, block_size=20):
        self.__board_size = board_size
        self.__block_size = block_size
        self.__game_speed = game_speed
        self.__game_state = GameState(board_size, board_size)
        self.__window = pygame.display.set_mode((self.__board_size*self.__block_size,
                                                 self.__board_size*self.__block_size))
        self.__fps = pygame.time.Clock()
        self.__score = 0
        self.__snake = self.__game_state.snake
        self.__food_spawn = self.__game_state.food_spawn
        self.__agent = self.get_agent(agent)

    def get_agent(self, agent):
        if agent is None:
            return None
        elif agent.upper() == "RANDOM":
            return RandomSearchAgent()
        elif agent.upper() == "ZIGZAG":
            return ZigZagSearchAgent(EatFoodProblem(self.__game_state))
        elif agent.upper() == "SMART":
            return SmartSearchAgent(EatFoodProblem(self.__game_state))
        elif agent.upper() == "OROBORUS":
            return OroborusSearchAgent(ReachPositionProblem(self.__game_state))
        elif agent.upper() == "MC":
            return MCAgent(self.__game_state)
        return None

    def draw_new_state(self, food_pos):
        """
        Draw new game state on screen.
        :param food_pos: current food position.
        """
        self.__window.fill(pygame.Color(225, 225, 225))
        # Draw snake
        head = 1
        for pos in self.__snake.body:
            if head == 1:
                pygame.draw.rect(self.__window, HEAD_COLOR, pygame.Rect(pos[0] * self.__block_size,
                                                                        pos[1] * self.__block_size,
                                                                        self.__block_size,
                                                                        self.__block_size))
                head = 0
            else:
                pygame.draw.rect(self.__window, BODY_COLOR, pygame.Rect(pos[0] * self.__block_size,
                                                                        pos[1] * self.__block_size,
                                                                        self.__block_size,
                                                                        self.__block_size))
        # Draw food
        pygame.draw.rect(self.__window, FOOD_COLOR, pygame.Rect(food_pos[0] * self.__block_size,
                                                                food_pos[1] * self.__block_size,
                                                                self.__block_size,
                                                                self.__block_size))

    def game_over(self):
        pygame.display.set_caption("Score: " + str(self.__score) +
                                   " | GAME OVER. Press any key to quit ...")
        while True:
            evt = pygame.event.wait()
            if evt.type == pygame.KEYDOWN:
                break
            pygame.quit()
            sys.exit()

    def update(self):
        pygame.display.set_caption("Score: " + str(self.__score))
        pygame.display.flip()
        self.__fps.tick(self.__game_speed)

    @abstractmethod
    def start_game(self):
        pass

    @property
    def score(self):
        return self.__score

    @score.setter
    def score(self, value):
        self.__score = value

    @property
    def fps(self):
        return self.__fps

    @property
    def food_spawn(self):
        return self.__food_spawn

    @food_spawn.setter
    def food_spawn(self, value):
        self.__food_spawn = value

    @property
    def snake(self):
        return self.__snake

    @snake.setter
    def snake(self, value):
        self.__snake = value

    @property
    def agent(self):
        return self.__agent

    @agent.setter
    def agent(self, value):
        self.__agent = value

    @property
    def game_state(self):
        return self.__game_state

    @game_state.setter
    def game_state(self, value):
        self.__game_state = value


class ManualGame(Game):

    def __init__(self, board_size, agent=None):
        super().__init__(board_size, agent)

    def __update_snake(self):
        """
        Update snake position.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game_over()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    self.snake.change_direction(DIRECTION.RIGHT)
                elif event.key == pygame.K_UP:
                    self.snake.change_direction(DIRECTION.UP)
                elif event.key == pygame.K_DOWN:
                    self.snake.change_direction(DIRECTION.DOWN)
                elif event.key == pygame.K_LEFT:
                    self.snake.change_direction(DIRECTION.LEFT)

    def start_game(self):
        while True:
            food_pos = self.food_spawn.spawn_food(self.game_state.empty_cells())
            self.__update_snake()

            if self.snake.move(food_pos) == 1:
                self.score += 1
                self.food_spawn.set_food_on_board(False)

            self.draw_new_state(food_pos)

            if self.snake.check_collision():
                self.game_over()
                break

            self.update()


class SmartAgentsGame(Game):

    def __init__(self, board_size, agent=None, game_speed=10, block_size=20):
        super().__init__(board_size, agent, game_speed, block_size)

    def start_game(self):
        while True:
            self.snake.change_direction(self.agent.get_next_action())
            food_pos = self.food_spawn.spawn_food(self.game_state.empty_cells())

            if self.snake.move(food_pos) == 1:
                self.score += 1
                self.food_spawn.set_food_on_board(False)
                self.draw_new_state(food_pos)
                if self.snake.check_collision():
                    self.game_over()
                    break
                self.food_spawn.spawn_food(self.game_state.empty_cells())
                self.agent.problem.reset(self.game_state)
                self.agent.update()
            else:
                self.draw_new_state(food_pos)

                if self.snake.check_collision():
                    self.game_over()
                    break
                if self.agent.problem is not None:
                    self.agent.problem.reset(self.game_state)
                self.agent.update()

            self.update()


class OroborusAgentGame(Game):

    def __init__(self, board_size, agent=None, game_speed=10, block_size=20):
        super().__init__(board_size, agent, game_speed, block_size)

    def start_game(self):
        while True:
            if self.agent.action_count() == 0:
                self.agent.problem.reset(self.game_state)
                self.agent.update()
            self.snake.change_direction(self.agent.get_next_action())
            food_pos = self.food_spawn.spawn_food(self.game_state.empty_cells())
            if food_pos is None:
                self.game_over()
                break
            if self.snake.move(food_pos) == 1:
                self.score += 1
                self.food_spawn.set_food_on_board(False)
                self.draw_new_state(food_pos)
                if self.snake.check_collision():
                    self.game_over()
                    break
                self.food_spawn.spawn_food(self.game_state.empty_cells())
            else:
                self.draw_new_state(food_pos)
                if self.snake.check_collision():
                    self.game_over()
                    break

            self.update()


class GeneralAgentGame(Game):

    def __init__(self, board_size, agent=None, game_speed=10, block_size=20):
        super().__init__(board_size, agent, game_speed, block_size)

    def start_game(self):
        while True:
            self.snake.change_direction(self.agent.get_next_action())
            food_pos = self.food_spawn.spawn_food(self.game_state.empty_cells())

            if self.snake.move(food_pos) == 1:
                self.score += 1
                self.food_spawn.set_food_on_board(False)
                self.draw_new_state(food_pos)
                if self.snake.check_collision():
                    self.game_over()
                    break
                self.food_spawn.spawn_food(self.game_state.empty_cells())
            else:
                self.draw_new_state(food_pos)
                if self.snake.check_collision():
                    self.game_over()
                    break

            self.update()


class ReinforcementAgentsGame(Game):

    def __init__(self, board_size, agent=None, game_speed=10, block_size=20, episodes=100):
        super().__init__(board_size, agent, game_speed, block_size)
        self.agent = self.get_agent(agent)
        self.__episodes = episodes
        self.__counter = 0
        self.__scores = {}

    def get_agent(self, agent):
        if agent is None:
            return None
        elif agent.upper() == "Q":
            return QAgent(Environment(self.game_state))
        elif agent.upper() == "MCQ":
            return MCQAgent(Environment(self.game_state))
        return None

    def start_game(self):
        while True:
            if self.__counter == self.__episodes:
                break
            action = self.agent.get_next_action()
            self.snake.change_direction(action)
            self.agent.current_action = action
            food_pos = self.food_spawn.food

            if self.snake.move(food_pos) == 1:
                self.agent.current_reward = self.agent.environment.get_reward()
                self.agent.update()
                self.score += 1
                self.food_spawn.set_food_on_board(False)
                food_pos = self.food_spawn.spawn_food(self.game_state.empty_cells())
                self.draw_new_state(food_pos)
                if self.snake.check_collision():
                    self.__reset()
                    self.draw_new_state(food_pos)
            else:
                self.agent.current_reward = self.agent.environment.get_reward()
                self.agent.update()
                self.draw_new_state(food_pos)

                if self.snake.check_collision():
                    self.__reset()
                    self.draw_new_state(food_pos)

            self.update()
        with open("q_agent_table.pickle", "wb+") as file:
            pickle.dump(self.agent.q_table, file)
        print(self.__scores)

    def __reset(self):
        self.game_state = GameState(self.game_state.height, self.game_state.width)
        print("Score:", self.score)
        if self.score in self.__scores.keys():
            self.__scores[self.score] += 1
        else:
            self.__scores[self.score] = 1
        self.score = 0
        self.snake = self.game_state.snake
        self.food_spawn = self.game_state.food_spawn
        self.agent.environment = Environment(self.game_state)
        self.agent.reset()
        self.__counter += 1
        print("Episode :", self.__counter)
