from parser import Parser
from pathfinder import Pathfinder

def main() -> None:

    graph = Parser.file_parser()

    print(Pathfinder.dijkstra(graph))

main()