from typing import Optional
from .zone import Zone
from .connection import Connection

class Graph:
    def __init__(self):
        self.nb_drones: int = 0
        self.start_hub: Optional[Zone] = None
        self.end_hub: Optional[Zone] = None
        self.hubs: dict[str, Zone] = {}
        self.connections: list[Connection] = []
        self.adjacency: dict[str, list[Zone]] = {}