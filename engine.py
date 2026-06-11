from models.connection import Connection
from models.graph import Graph
from models.drone import Drone
from models.zone import Zone
import heapq

class Engine:

    @staticmethod
    def next(graph: Graph, drone: Drone, base: dict[str, int]) -> Zone | None:

        def costcal(path: list[Zone]) -> int:
            cost = 0
            for hub in path:
                cost += hub.cost
            return cost

        heap = [(0, drone.position.name, [])]
        visited = set()
        heapq.heapify(heap)
        while heap:
            cost, hub, path = heapq.heappop(heap)
            if graph.hubs[hub].is_end:
                if base['f']:
                    base['base'] = costcal(drone.path + [graph.hubs[hub] for hub in path])
                    base['f'] = 0
                if costcal(drone.path + [graph.hubs[hub] for hub in path]) > base['base']:
                    return None
                else:
                    return graph.hubs[path[0]]
            if hub in visited:
                continue
            if len(path) == 1 and graph.hubs[hub].reserved:
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
        tmp = set()
        base = {'f': 1, 'base': 0}

        def connection(from_zone: Zone, to_zone: Zone) -> Connection:
            for conn in graph.connections:
                if from_zone is conn.from_zone and to_zone is conn.to_zone:
                    return conn
            return None

        while delivered < graph.nb_drones:
            line = ""
            i = 0
            while i < len(drones):
                if drones[i].delivered:
                    i += 1
                    continue

                elif drones[i] in tmp:
                    if not drones[i].position.reserved:
                        drones[i].position.capacity += 1
                        line += f"D{drones[i].id}-{drones[i].position} "
                        if drones[i].position.is_end:
                            drones[i].delivered = 1
                            delivered += 1
                        elif drones[i].position.capacity == drones[i].position.max_drones:
                            drones[i].position.reserved = 1

                        tmp.remove(drones[i])
                    i += 1
                    continue

                nxt = cls.next(graph, drones[i], base)
                if nxt:
                    if nxt.zone == 'restricted':
                        line += f"D{drones[i].id}-{drones[i].position}--{nxt} "
                        drones[i].position.reserved = 0
                        drones[i].position.capacity -= 1
                        drones[i].position = nxt
                        drones[i].path.append(nxt)
                        tmp.add(drones[i])
                        i += 1
                    else:
                        position = drones[i].position
                        nbs = []
                        for drone in drones:
                            if not drone.id == drones[i].id and drone.position.name == position.name:
                                nbs.append(drone.id)
                        drones[i].position.reserved = 0
                        drones[i].position.capacity -= 1
                        drones[i].position = nxt
                        drones[i].path.append(nxt)
                        drones[i].position.capacity += 1
                        line += f"D{drones[i].id}-{drones[i].position} "
                        if drones[i].position.is_end:
                            drones[i].delivered = 1
                            delivered += 1
                        elif drones[i].position.capacity == drones[i].position.max_drones:
                            drones[i].position.reserved = 1

                        if nbs:
                            conn = connection(position, nxt)
                            if conn:
                                for nb in nbs:
                                    while nxt.reserved == 0 and nxt.capacity < conn.max_link_capacity:
                                        if drones[nb] in tmp:
                                            tmp.remove(drones[nb])
                                        drones[nb].position = nxt
                                        drones[nb].path.append(nxt)
                                        drones[nb].position.capacity += 1
                                        line += f"D{drones[nb].id}-{drones[nb].position} "
                                        if drones[nb].position.is_end:
                                            drones[nb].delivered = 1
                                            delivered += 1
                                        elif nxt.capacity == nxt.max_drones:
                                            nxt.reserved = 1
                        i += 1
                else:
                    i += 1

            print(line)