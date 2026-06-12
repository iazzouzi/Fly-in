from parser import Parser
from engine import Engine

def main() -> None:

    graph = Parser.file_parser()

    turns = Engine.simulator(graph)

    # for turn in turns:
    #     print(turn)

main()