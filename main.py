from parser import Parser
from pathfinder import Pathfinder

def main() -> None:

    graph = Parser.file_parser()
    
    print(graph.nb_drones)

    print('\n', graph.start_hub, graph.start_hub.x, graph.start_hub.y, graph.start_hub.zone, graph.start_hub.color, graph.start_hub.max_drones, '\n')

    for hub in graph.hubs.values():
        print(hub, hub.x, hub.y, hub.zone, hub.color, hub.max_drones)

    print('\n', graph.end_hub, graph.end_hub.x, graph.end_hub.y, graph.end_hub.zone, graph.end_hub.color, graph.end_hub.max_drones, '\n')

    for conn in graph.connections:
        print(conn.from_zone, '->', conn.to_zone, conn.max_link_capacity)

    print()

    for key, value in graph.adjacency.items():
        print(key, [hub.name for hub in value])
    
    print(Pathfinder.dijkstra(graph))

main()