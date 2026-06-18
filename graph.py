from zone import Zone
from drone import Drone
from connection import Connection


class Graph:
    """Central data structure representing the drone routing network.

    Attributes:
        nb_drones (int): Total number of drones participating in the
            simulation.
        start_hub (Zone): The designated starting zone for all drones.
        end_hub (Zone): The designated destination zone for all drones.
        hubs (dict[str, Zone]): Dictionary mapping zone names to their
            Zone objects.
        connections (list[Connection]): Complete list of all valid
            bidirectional connections.
        adjacency (dict[str, list[Zone]]): Adjacency list mapping zone
            names to their directly connected neighbor Zones.
        drones (list[Drone]): Collection of all active Drone objects in
            the network.
    """

    def __init__(self) -> None:
        """Initializes an empty graph network."""
        self.nb_drones: int = 0
        self.start_hub: Zone
        self.end_hub: Zone
        self.hubs: dict[str, Zone] = {}
        self.connections: list[Connection] = []
        self.adjacency: dict[str, list[Zone]] = {}
        self.drones: list[Drone] = []
