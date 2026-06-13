from parser import Parser
from engine import Engine
# from visualizer import Visualizer

def main() -> None:

    graph = Parser.file_parser()

    turns = Engine.simulator(graph)

    # visualizer = Visualizer(graph, turns)
    # visualizer.run()

main()