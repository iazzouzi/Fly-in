from parser import Parser
from engine import Engine
from visualizer import Visualizer


def main() -> None:
    """Main entry point for the drone routing simulation.

    Workflow:
        1. Parses the input file to build the network graph.
        2. Runs the simulation engine to calculate drone movements.
        3. Visualizes the results in a graphical arcade interface.
    """
    graph = Parser.file_parser()
    turns = Engine.simulator(graph)
    Visualizer.run(1960, 1080, graph, turns)


main()
