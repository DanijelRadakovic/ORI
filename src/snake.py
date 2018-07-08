import getopt
from game import *

SIZES = {"XXS": 5, "XS": 8, "S": 16, "M": 26, "L": 30}
AGENTS = ["RANDOM", "ZIGZAG", "SMART", "OROBORUS", "Q", "MC", "MCQ"]


def parse_args(argv):
    """
    Parse program arguments.
    :param argv: list of strings that represent program arguments.
    :return: chosen algorithm, game board size and agent.
    """
    try:
        opts, args = getopt.getopt(argv, "ha:s:", ["help", "agent=", "size="])
    except getopt.GetoptError:
        print("Wrong arguments")
        print("snake.py -a <agent> -s <size>")
        sys.exit(2)

    if len(opts) == 0:
        return "MANUAL", SIZES["LARGE"]

    snake_agent, board_size = "", 0
    for opt, arg in opts:
        if opt == "-h":
            print("snake.py -a <agent> -s <size>")
            sys.exit()
        elif opt in ("-a", "agent"):
            snake_agent = arg
            if snake_agent.upper() not in AGENTS:
                message = "Allowed values for -a (agent) argument are:"
                for i in AGENTS:
                    message += i + " "
                print(message)
                sys.exit(2)
    for opt, arg in opts:
        if opt in ("-s", "size"):
            board_size = arg
            if board_size.upper() not in SIZES.keys():
                message = "Allowed values for -s (size) argument are: "
                for i in SIZES:
                    message += i + " "
                print(message)
                sys.exit(2)
            else:
                if snake_agent.upper() == "Q":
                    if board_size.upper() == "M" or board_size.upper() == "L":
                        board_size = SIZES["XS"]
                    elif board_size.upper() == "S":
                        board_size = SIZES["XXS"]
                    else:
                        board_size = SIZES[board_size.upper()]
                elif snake_agent.upper() == "OROBORUS" and board_size.upper() == "XXS":
                    board_size = SIZES["XS"]
                else:
                    board_size = SIZES[board_size.upper()]
    return snake_agent, board_size


if __name__ == '__main__':
    agent, size = parse_args(sys.argv[1:])
    if size == SIZES["XXS"] or size == SIZES["XS"]:
        block_size = 50
    else:
        block_size = 20
    if agent == "MANUAL":
        game = ManualGame(size)
    elif agent.upper() == "ZIGZAG" or agent.upper() == "SMART" or agent.upper() == "RANDOM":
        game = SmartAgentsGame(size, agent, 10, block_size)
    elif agent.upper() == "OROBORUS":
        game = OroborusAgentGame(size, agent, 30, block_size)
    elif agent.upper() == "MC":
        game = GeneralAgentGame(size, agent, 10, block_size)
    elif agent.upper() == "Q" or agent.upper() == "MCQ":
        game = ReinforcementAgentsGame(size, agent, 10, block_size, 30)
    else:
        game = ManualGame(size)
    game.start_game()
