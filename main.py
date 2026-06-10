from parser import Parser
from engine import Engine

def main() -> None:

    graph = Parser.file_parser()

    Engine.simulator(graph)


main()