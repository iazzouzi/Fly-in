from zone import Zone
from drone import Drone
from connection import Connection


class Graph:
    """Central data structure representing the entire drone routing network.

    Populated incrementally by :class:`~parser.Parser` and then consumed
    by :class:`~engine.Engine`.  The adjacency list is built at the end of
    parsing so that pathfinding can iterate neighbours without scanning
    the full connection list each time.

    Attributes:
        nb_drones: Total number of drones to be simulated, as specified by
            the ``nb_drones`` line in the map file.
        start_hub: The unique starting zone; set by the parser when a
            ``start_hub`` line is encountered.
        end_hub: The unique destination zone; set by the parser when an
            ``end_hub`` line is encountered.
        hubs: Mapping of zone name → :class:`~zone.Zone` for every zone
            defined in the map file (start, end, and regular hubs).
        connections: Ordered list of all :class:`~connection.Connection`
            objects, preserving parse order.
        adjacency: Adjacency list mapping each zone name to the list of
            directly reachable neighbouring :class:`~zone.Zone` objects.
            Built by :meth:`~parser.Parser.file_parser` after all zones
            and connections have been parsed.
        drones: Collection of all :class:`~drone.Drone` instances spawned
            by the engine; populated during simulation initialisation.
    """

    def __init__(self) -> None:
        """Initialises an empty graph with default/empty containers."""
        self.nb_drones: int = 0
        self.start_hub: Zone
        self.end_hub: Zone
        self.hubs: dict[str, Zone] = {}
        self.connections: list[Connection] = []
        self.adjacency: dict[str, list[Zone]] = {}
        self.drones: list[Drone] = []
