from parser import Parser
from engine import Engine
from visualizer import Visualizer

def main() -> None:

    graph = Parser.file_parser()

    turns = Engine.simulator(graph)

    Visualizer.run(1960, 1080, graph, turns)

main()