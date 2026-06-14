from zone import Zone
from connection import Connection

class Graph:
    def __init__(self) -> None:
        self.nb_drones: int = 0
        self.start_hub: Zone
        self.end_hub: Zone
        self.hubs: dict[str, Zone] = {}
        self.connections: list[Connection] = []
        self.adjacency: dict[str, list[Zone]] = {}