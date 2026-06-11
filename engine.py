from models.connection import Connection
from models.graph import Graph
from models.drone import Drone
from models.zone import Zone
import heapq

class Engine:

    @staticmethod
    def next(graph: Graph, drone: Drone, base: dict[str, float]) -> Zone | None:
        def costcal(path: list[Zone]) -> float:
            cost = 0.0
            for hub in path:
                cost += hub.cost
            return cost
        heap: list[tuple[float, str, list[str]]] = [(0.0, drone.position.name, [])]
        visited = set()
        heapq.heapify(heap)
        while heap:
            cost, hub, path = heapq.heappop(heap)
            zone = graph.hubs[hub]
            if zone.is_end:
                if base['f']:
                    base['base'] = costcal(drone.path + [graph.hubs[hub] for hub in path])
                    base['f'] = 0
                if costcal(drone.path + [graph.hubs[hub] for hub in path]) > base['base']:
                    return None
                else:
                    return graph.hubs[path[0]]
            if hub in visited:
                continue
            if len(path) == 1 and zone.reserved:
                continue
            visited.add(hub)
            for neighbor in graph.adjacency[hub]:
                if neighbor.zone == 'blocked':
                    continue
                heapq.heappush(heap, (cost + neighbor.cost, neighbor.name, path + [neighbor.name]))
        return None


    @classmethod
    def simulator(cls, graph: Graph) -> None:
        drones: list[Drone] = [Drone(i, [], graph.start_hub) for i in range(1, graph.nb_drones+1)]
        delivered = 0
        tmp: set[Drone] = set()
        base = {'f': 1, 'base': 0.0}
        while delivered < graph.nb_drones:
            line = ""
            i = 0
            while i < len(drones):
                pos = drones[i].position
                if drones[i].delivered:
                    i += 1
                    continue
                elif drones[i] in tmp:
                    if not pos.reserved:
                        pos.occupancy.append(drones[i])
                        line += f"D{drones[i].id}-{pos} "
                        if pos.is_end:
                            drones[i].delivered = 1
                            delivered += 1
                        elif len(pos.occupancy) == pos.max_drones:
                            pos.reserved = 1
                        tmp.remove(drones[i])
                    i += 1
                    continue
                nxt = cls.next(graph, drones[i], base)
                if nxt:
                    if nxt.zone == 'restricted':
                        line += f"D{drones[i].id}-{pos}--{nxt} "
                        pos.reserved = 0
                        if drones[i] in pos.occupancy:
                            pos.occupancy.remove(drones[i])
                        drones[i].position = nxt
                        drones[i].path.append(nxt)
                        tmp.add(drones[i])
                        i += 1
                    else:
                        line += f"D{drones[i].id}-{nxt} "
                        pos.reserved = 0
                        if drones[i] in pos.occupancy:
                            pos.occupancy.remove(drones[i])
                        drones[i].position = nxt
                        drones[i].path.append(nxt)
                        drones[i].position.occupancy.append(drones[i])
                        if drones[i].position.is_end:
                            drones[i].delivered = 1
                            delivered += 1
                        elif len(drones[i].position.occupancy) == drones[i].position.max_drones:
                            drones[i].position.reserved = 1
                        i += 1
                else:
                    i += 1
            print(line)