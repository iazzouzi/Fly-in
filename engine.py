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
        graph: Graph,
        drone: Drone,
        base: dict[str, int | float | list[list[str]]]
    ) -> Zone | None:
        """Finds the optimal next zone for a drone using Dijkstra's algorithm.

        Implements pathfinding that respects zone types and movement costs.
        Uses a priority queue to explore the cheapest paths first.

        Args:
            graph (Graph): The network graph containing zones and connections.
            drone (Drone): The drone requiring a path calculation.
            base (dict[str, int | float | list[list[str]]]): Shared state
                dictionary with three keys: 'f' (int flag, 1 on first call
                then set to 0 after the baseline cost is recorded), 'base'
                (float storing the reference path cost all drones must match),
                and 'cache' (list of previously computed [from, next] name
                pairs for fast lookup without re-running Dijkstra).

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

        assert isinstance(base['cache'], list)
        for path in base['cache']:
            if (drone.position.name == path[0]
                    and not graph.hubs[path[1]].reserved):
                return graph.hubs[path[1]]

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

                base['cache'].append([drone.position.name] + path)
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

        if drone.position.is_start and drone.id == 1:
            raise SystemExit(
                f"No valid path found for Drone {drone.id} from start zone."
            )
        return None

    @classmethod
    def simulator(
        cls, graph: Graph
    ) -> list[list[dict[str, list[Drone] | Zone | int]]]:
        """Runs the simulation to route all drones from start to end.

        Executes turn-by-turn simulation, scheduling drone movements while
        respecting capacity constraints, restricted zones, and connection
        limits. Uses two sets to coordinate movement within each turn:
        `stmp` tracks drones already moved this turn (preventing double
        moves), and `tmp` tracks drones mid-transit through restricted zones
        that must complete their journey on the next turn.

        Args:
            graph (Graph): The fully parsed network graph.

        Returns:
            list[list[dict[str, list[Drone] | Zone | int]]]: A chronological
                timeline of turns, where each turn contains movement
                dictionaries tracking drone transitions for the visualizer.
        """
        def get_conn_capacity(zone_a: Zone, zone_b: Zone) -> int:
            """Retrieves the maximum connection capacity between two zones.

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
            drone.path.append(graph.start_hub)
            graph.drones.append(drone)
            graph.start_hub.occupancy.append(drone)

        turns: list[list[dict[str, list[Drone] | Zone | int]]] = []
        delivered = 0
        tmp: set[Drone] = set()
        base: dict[str, int | float | list[list[str]]] = {
            'f': 1,
            'base': 0.0,
            'cache': []
        }

        while delivered < graph.nb_drones:
            turns.append([])
            stmp: set[Drone] = set()
            line = ""
            i = 0
            f = 0

            while i < len(drones):
                drone = drones[i]

                if drone.delivered or drone in stmp:
                    i += 1
                    continue
                if graph.nb_drones > 100:
                    for zone in graph.adjacency[drone.position.name]:
                        if zone is not drone.position and not zone.reserved:
                            break
                    else:
                        f = 1
                    if f:
                        break

                pos = drone.position

                if drone in tmp:
                    line += f"D{drone.id}-{pos} "
                    turns[-1].append({
                        'drones': [drone],
                        'from': drone.path[-2],
                        'to': pos,
                        'cost2': 0,
                        'f': 1,
                    })
                    if pos.is_end:
                        drone.delivered = 1
                        delivered += 1
                    tmp.remove(drone)
                    i += 1
                    continue

                nxt = cls.next(graph, drone, base)
                if nxt:
                    conn_capacity = get_conn_capacity(pos, nxt)
                    turns[-1].append({
                        'drones': [],
                        'from': pos,
                        'to': nxt,
                        'cost2': 0,
                        'f': 0,
                    })
                    u = 0
                    for drone in pos.occupancy:
                        if u >= conn_capacity or nxt.reserved:
                            break
                        if drone in stmp:
                            continue
                        if nxt.zone == 'restricted':
                            line += f"D{drone.id}-{pos}-{nxt} "
                            turns[-1][-1]['cost2'] = 1
                            nxt.reserved = 1
                            tmp.add(drone)
                        else:
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
                    i += 1

            if line:
                print(line.strip())

        return turns
