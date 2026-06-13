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
                if costcal(drone.path + [graph.hubs[hub] for hub in path]) != base['base']:
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
    def simulator(cls, graph: Graph) -> list[list[tuple[int, Zone, Zone, int]]]:
        def get_conn_capacity(from_zone, to_zone) -> int:
            for conn in graph.connections:
                if conn.from_zone is from_zone and conn.to_zone is to_zone:
                    return conn.max_link_capacity
        drones: list[Drone] = [Drone(i, [], graph.start_hub) for i in range(1, graph.nb_drones+1)]
        for drone in drones:
            graph.start_hub.occupancy.append(drone)
        turns: list[list[tuple[int, Zone, Zone, int]]] = []
        delivered = 0
        tmp: set[Drone] = set()
        base = {'f': 1, 'base': 0.0}
        while delivered < graph.nb_drones:
            turns.append([])
            stmp = set()
            line = ""
            i = 0
            while i < len(drones):
                if drones[i].delivered or drones[i] in stmp:
                    i += 1
                    continue
                pos = drones[i].position
                if drones[i] in tmp:
                    line += f"D{drones[i].id}-{pos} "
                    if pos.is_end:
                        drones[i].delivered = 1
                        delivered += 1
                    tmp.remove(drones[i])
                    i += 1
                    continue
                nxt = cls.next(graph, drones[i], base)
                if nxt:
                    if nxt.zone == 'restricted':
                        line += f"D{drones[i].id}-{pos}--{nxt} "
                        turns[-1].append((drones[i].id, pos, nxt, 1))
                        pos.reserved = 0
                        pos.occupancy.remove(drones[i])
                        drones[i].position = nxt
                        drones[i].path.append(nxt)
                        nxt.reserved = 1
                        nxt.occupancy.append(drones[i])
                        tmp.add(drones[i])
                        stmp.add(drones[i])
                        i += 1
                    else:
                        if len(pos.occupancy) > 1 and nxt.max_drones > 1 and get_conn_capacity(pos, nxt) > 1:
                            conn_capacity = get_conn_capacity(pos, nxt)
                            tmp_list = []
                            u = 0
                            while u <= len(pos.occupancy) and u < conn_capacity and nxt.reserved == 0:
                                drone = pos.occupancy[0]
                                if drone in stmp:
                                    u += 1
                                    continue
                                line += f"D{drone.id}-"
                                tmp_list.append(drone.id)
                                pos.reserved = 0
                                pos.occupancy.remove(drone)
                                drone.position = nxt
                                drone.path.append(nxt)
                                nxt.occupancy.append(drone)
                                if nxt.is_end:
                                    drone.delivered = 1
                                    delivered += 1
                                elif len(nxt.occupancy) == nxt.max_drones:
                                    nxt.reserved = 1
                                stmp.add(drone)
                                u += 1
                            line += f"{nxt} "
                            tmp_list += [pos, nxt, 0]
                            turns[-1].append(tuple(tmp_list))
                            i += 1
                        else:
                            line += f"D{drones[i].id}-{nxt} "
                            turns[-1].append((drones[i].id, pos, nxt, 0))
                            pos.reserved = 0
                            pos.occupancy.remove(drones[i])
                            drones[i].position = nxt
                            drones[i].path.append(nxt)
                            nxt.occupancy.append(drones[i])
                            if nxt.is_end:
                                drones[i].delivered = 1
                                delivered += 1
                            elif len(nxt.occupancy) == nxt.max_drones:
                                nxt.reserved = 1
                            stmp.add(drones[i])
                            i += 1
                else:
                    i += 1
            print(line)
        return turns