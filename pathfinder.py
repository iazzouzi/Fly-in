from models.connection import Connection
from models.graph import Graph
from models.zone import Zone
import heapq


class Pathfinder:
    @staticmethod
    def dijkstra(graph: Graph) -> list[str]:
        start = graph.start_hub
        heap = [(0, start.name, [start.name])]
        visited = set()
        heapq.heapify(heap)
        while heap:
            zone = heapq.heappop(heap)
            if graph.hubs[zone[1]].is_end:
                return zone[2]
            if zone[1] in visited:
                continue
            visited.add(zone[1])
            for neighbor in graph.adjacency[zone[1]]:
                if neighbor.zone == 'blocked':
                    continue
                heapq.heappush(heap, (zone[0] + neighbor.cost, neighbor.name, zone[2] + [neighbor.name]))
        raise SystemExit(f"No path found from {graph.start_hub.name} to {graph.end_hub.name}")