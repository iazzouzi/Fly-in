import heapq
from graph import Graph
from drone import Drone
from zone import Zone


class Engine:
    """Simulation engine for managing drone routing and movement.

    This class handles the core simulation logic including pathfinding,
    movement scheduling, and turn-based simulation of drone delivery.
    """

    @staticmethod
    def next(
        graph: Graph, drone: Drone, base: dict[str, float]
    ) -> Zone | None:
        """Finds the optimal next zone for a drone using Dijkstra's algorithm.

        Implements pathfinding that respects zone types and movement costs.
        Uses a priority queue to explore the cheapest paths first.

        Args:
            graph (Graph): The network graph containing zones and connections.
            drone (Drone): The drone requiring a path calculation.
            base (dict[str, float]): Dictionary tracking base path cost for
                consistency.

        Returns:
            Zone | None: The next zone the drone should move to, or None if
                no valid path exists or if the path cost differs from the
                base cost.
        """
        def costcal(path: list[Zone]) -> float:
            """Calculates total movement cost for a specific path.

            Args:
                path (list[Zone]): Chronological list of zones to evaluate.

            Returns:
                float: Total accumulated cost.
            """
            cost = 0.0
            for hub in path:
                cost += hub.cost
            return cost

        heap: list[tuple[float, str, list[str]]] = [
            (0.0, drone.position.name, [])
        ]
        visited = set()
        heapq.heapify(heap)

        while heap:
            cost, hub, path = heapq.heappop(heap)
            zone = graph.hubs[hub]

            if zone.is_end:
                if base['f']:
                    base['base'] = costcal(
                        drone.path + [graph.hubs[h] for h in path]
                    )
                    base['f'] = 0

                if costcal(
                    drone.path + [graph.hubs[h] for h in path]
                ) != base['base']:
                    return None
                return graph.hubs[path[0]]

            if hub in visited:
                continue

            if len(path) == 1 and zone.reserved:
                continue

            visited.add(hub)

            for neighbor in graph.adjacency[hub]:
                if neighbor.zone == 'blocked':
                    continue
                heapq.heappush(
                    heap,
                    (
                        cost + neighbor.cost,
                        neighbor.name,
                        path + [neighbor.name]
                    ),
                )

        return None

    @classmethod
    def simulator(
        cls, graph: Graph
    ) -> list[list[dict[str, list[Drone] | Zone | int]]]:
        """Runs the simulation to route all drones from start to end.

        Executes turn-by-turn simulation, scheduling drone movements while
        respecting capacity constraints, restricted zones, and connection
        limits.

        Args:
            graph (Graph): The fully parsed network graph.

        Returns:
            list[list[dict[str, list[Drone] | Zone | int]]]: A chronological
                timeline of turns, where each turn contains movement
                dictionaries tracking drone transitions for the visualizer.
        """
        def get_conn_capacity(zone_a: Zone, zone_b: Zone) -> int:
            """Retrieves the maximum capacity of a connection
            between two zones.

            Args:
                zone_a (Zone): The first zone.
                zone_b (Zone): The second zone.

            Returns:
                int: Maximum number of drones allowed on the connection.
            """
            for conn in graph.connections:
                if (
                    (conn.from_zone is zone_a and conn.to_zone is zone_b)
                    or (conn.from_zone is zone_b and conn.to_zone is zone_a)
                ):
                    return conn.max_link_capacity
            return 1

        drones: list[Drone] = [
            Drone(i, [], graph.start_hub)
            for i in range(1, graph.nb_drones + 1)
        ]

        for drone in drones:
            drone.x = graph.start_hub.x
            drone.y = graph.start_hub.y
            graph.drones.append(drone)
            graph.start_hub.occupancy.append(drone)

        turns: list[list[dict[str, list[Drone] | Zone | int]]] = []
        delivered = 0
        tmp: set[Drone] = set()
        base = {'f': 1, 'base': 0.0}

        while delivered < graph.nb_drones:
            turns.append([])
            stmp: set[Drone] = set()
            line = ""
            i = 0

            while i < len(drones):
                current_drone = drones[i]

                if current_drone.delivered or current_drone in stmp:
                    i += 1
                    continue

                pos = current_drone.position

                if current_drone in tmp:
                    line += f"D{current_drone.id}-{pos} "
                    turns[-1].append({
                        'drones': [current_drone],
                        'from': current_drone.path[-2],
                        'to': pos,
                        'cost2': 0,
                        'f': 1,
                    })
                    if pos.is_end:
                        current_drone.delivered = 1
                        delivered += 1
                    tmp.remove(current_drone)
                    i += 1
                    continue

                nxt = cls.next(graph, current_drone, base)

                if nxt:
                    if nxt.zone == 'restricted':
                        line += f"D{current_drone.id}-{pos.name}-{nxt.name} "
                        turns[-1].append({
                            'drones': [current_drone],
                            'from': pos,
                            'to': nxt,
                            'cost2': 1,
                            'f': 0,
                        })
                        pos.reserved = 0
                        pos.occupancy.remove(current_drone)
                        current_drone.position = nxt
                        current_drone.path.append(nxt)
                        nxt.reserved = 1
                        nxt.occupancy.append(current_drone)
                        tmp.add(current_drone)
                        stmp.add(current_drone)
                        i += 1

                    else:
                        conn_capacity = get_conn_capacity(pos, nxt)
                        if (
                            len(pos.occupancy) > 1
                            and nxt.max_drones > 1
                            and conn_capacity > 1
                        ):
                            turns[-1].append({
                                'drones': [],
                                'from': pos,
                                'to': nxt,
                                'cost2': 0,
                                'f': 0,
                            })

                            u = 0
                            for drone in list(pos.occupancy):
                                if u >= conn_capacity or nxt.reserved:
                                    break
                                if drone in stmp:
                                    continue

                                line += f"D{drone.id}-{nxt.name} "
                                drn_list = turns[-1][-1]['drones']
                                assert isinstance(drn_list, list)
                                drn_list.append(drone)

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
                            i += 1
                        else:
                            line += f"D{current_drone.id}-{nxt.name} "
                            turns[-1].append({
                                'drones': [current_drone],
                                'from': pos,
                                'to': nxt,
                                'cost2': 0,
                                'f': 0,
                            })
                            pos.reserved = 0
                            pos.occupancy.remove(current_drone)
                            current_drone.position = nxt
                            current_drone.path.append(nxt)
                            nxt.occupancy.append(current_drone)

                            if nxt.is_end:
                                current_drone.delivered = 1
                                delivered += 1
                            elif len(nxt.occupancy) == nxt.max_drones:
                                nxt.reserved = 1

                            stmp.add(current_drone)
                            i += 1
                else:
                    i += 1

            if line:
                print(line.strip())

        return turns
