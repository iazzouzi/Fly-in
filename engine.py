import heapq
from graph import Graph
from drone import Drone
from zone import Zone


class Engine:
    """Turn-based simulation engine that routes all drones to the end hub.

    Provides two static methods: :meth:`next` computes the optimal next
    zone for a single drone using Dijkstra's algorithm with caching, and
    :meth:`simulator` orchestrates the full multi-turn simulation while
    enforcing all capacity, occupancy, and restricted-zone transit rules.
    """

    @staticmethod
    def next(
        graph: Graph,
        drone: Drone,
        base: dict[str, int | float | list[list[str]]]
    ) -> Zone | None:
        """Returns the best next zone for *drone*, or ``None`` if blocked.

        Runs Dijkstra from the drone's current position to the ``end_hub``,
        weighting edges by the destination zone's ``cost`` attribute.
        Results are stored in a shared cache so subsequent calls for the
        same ``(current_zone, next_zone)`` pair skip the heap entirely.

        The first drone to reach the goal sets the **base cost** — a
        reference total path cost that all subsequent drones must match.
        This ensures drones are distributed across paths of equal length
        rather than all converging on a single shortest route.

        Args:
            graph: The network graph containing zones, adjacency, and
                connection data.
            drone: The drone requesting a next-step decision.
            base: Shared mutable state dictionary with three keys:

                * ``'f'`` (``int``) — ``1`` until the first Dijkstra
                  solution sets the baseline, then ``0``.
                * ``'base'`` (``float``) — reference cumulative path cost
                  that every drone's trajectory must equal.
                * ``'cache'`` (``list[list[str]]``) — each entry is
                  ``[current_zone_name, next_zone_name]``, looked up
                  before running Dijkstra.

        Returns:
            The :class:`~zone.Zone` the drone should move into this turn,
            or ``None`` if no valid unblocked path exists or if the only
            available path deviates from the base cost.
        """
        def costcal(path: list[Zone]) -> float:
            """Sums the ``cost`` attribute of every zone in *path*.

            Args:
                path: Ordered sequence of zones to evaluate.

            Returns:
                Total accumulated movement cost as a float.
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
                f"No valid path found for Drone {drone.id} from "
                f"'{drone.position.name}' to the end hub."
            )
        return None

    @classmethod
    def simulator(
        cls, graph: Graph
    ) -> list[list[dict[str, list[Drone] | Zone | int]]]:
        """Runs the full simulation and returns a per-turn movement timeline.

        Spawns all drones at the ``start_hub``, then iterates turn by turn
        until every drone has been delivered to the ``end_hub``.  Within
        each turn, drones are processed in ID order subject to:

        * **Zone capacity** — a zone must have room (accounting for drones
          leaving on the same turn) before a drone may enter.
        * **Connection capacity** — at most ``max_link_capacity`` drones
          may cross a given link in one turn.
        * **Restricted-zone transit** — moving toward a ``restricted`` zone
          costs 2 turns.  On turn 1 the drone is placed in *tmp* and the
          connection is logged; on turn 2 the drone completes the journey.
          A drone in *tmp* **must** move on the next turn and cannot wait.
        * **``stmp``** — a per-turn set that prevents a drone from being
          moved more than once in the same turn.
        * **Large-fleet shortcut** — when ``nb_drones > 100``, any drone
          with no free neighbour is skipped immediately to avoid O(N²)
          stalling scans.

        Args:
            graph: The fully parsed and validated network graph.

        Returns:
            A list of turns, where each turn is a list of movement dicts.
            Each dict contains:

            * ``'drones'`` — list of :class:`~drone.Drone` objects that
              moved along this edge.
            * ``'from'`` — source :class:`~zone.Zone`.
            * ``'to'`` — destination :class:`~zone.Zone`.
            * ``'cost2'`` — ``1`` if this is the first leg of a restricted
              transit (drone stops mid-edge), ``0`` otherwise.
            * ``'f'`` — ``1`` if this is the second leg of a restricted
              transit (drone departs from mid-edge), ``0`` otherwise.
        """
        def get_conn_capacity(zone_a: Zone, zone_b: Zone) -> int:
            """Returns the ``max_link_capacity`` between two adjacent zones.

            Args:
                zone_a: One endpoint of the connection.
                zone_b: The other endpoint of the connection.

            Returns:
                The connection's capacity limit, or ``1`` if the connection
                is not found (safe fallback).
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
                    for drone in list(pos.occupancy):
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
