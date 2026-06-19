from parser import Parser
from engine import Engine
from visualizer import Visualizer


def main() -> None:
    """Entry point for the Fly-in drone routing simulation.

    Executes the three-stage pipeline:

    1. **Parse** — reads and validates the map file (path from ``argv[1]``
       or interactive prompt), producing a fully linked :class:`~graph.Graph`.
    2. **Simulate** — runs the turn-based engine, printing each turn's
       drone movements to stdout in the required ``D<id>-<zone>`` format
       and returning the movement timeline.
    3. **Visualise** — opens the arcade window to replay the computed
       simulation with interactive playback controls.
    """
    graph = Parser.file_parser()
    turns = Engine.simulator(graph)
    Visualizer.run(1960, 1080, graph, turns)


main()
