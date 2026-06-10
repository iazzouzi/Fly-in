from models.connection import Connection
from models.graph import Graph
from models.drone import Drone
from models.zone import Zone
import heapq

class Engine:

    @staticmethod
    def next(graph: Graph, start: Zone) -> str | None:
        heap = [(0, start.name, [])]
        visited = set()
        heapq.heapify(heap)
        while heap:
            cost, name, path = heapq.heappop(heap)
            if graph.hubs[name].is_end:
                return path[0]
            if name in visited:
                continue
            if len(path) == 1 and graph.hubs[name].reserved:
                continue
            visited.add(name)
            for neighbor in graph.adjacency[name]:
                if neighbor.zone == 'blocked':
                    continue
                heapq.heappush(heap, (cost + neighbor.cost, neighbor.name, path + [neighbor.name]))
        return None


    @classmethod
    def simulator(cls, graph: Graph) -> None:
        drones: list[Drone] = [Drone(i, [], graph.start_hub) for i in range(1, graph.nb_drones+1)]
        delivered = 0
        tmp = set()
        bilal = []
        while delivered < graph.nb_drones:
            line = ""
            bilal.append([])
            for drone in drones:
                if drone.delivered:
                    continue
                if not drone.position:
                    drone.position = graph.hubs[drone.path[-1]]
                else:
                    if drone.position.capacity:
                        drone.position.capacity -= 1
                    if drone.position.reserved:
                        drone.position.reserved = 0
                nxt = cls.next(graph, drone.position)
                if nxt:
                    if graph.hubs[nxt].cost == 2 and not drone.id in tmp:
                        line += f"D{drone.id}-{drone.position}--{nxt} "
                        # bilal[-1].append((drone, drone.position, graph.hubs[nxt]))
                        drone.position.reserved = 0
                        drone.position.capacity -= 1
                        drone.position = None
                        tmp.add(drone.id)
                    else:
                        # bilal[-1].append((drone, drone.position, graph.hubs[nxt]))
                        if drone.id in tmp:
                            tmp.remove(drone.id)
                        drone.position = graph.hubs[nxt]
                        drone.position.capacity += 1
                        drone.path.append(drone.position.name)
                        line += f"D{drone.id}-{drone.position} "
                    
                        if drone.position.is_end:
                            drone.delivered = 1
                            delivered += 1
                        else:
                            if drone.position.capacity == drone.position.max_drones:
                                drone.position.reserved = 1

            print(line)
            # for mve in bilal:
            #     print(mve)