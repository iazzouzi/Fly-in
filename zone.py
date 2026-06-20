

class Zone:
    """A discrete node in the drone routing network (a "hub" in map files).

    Each zone has a type that governs movement cost, a capacity limit, an
    optional display colour, and runtime state tracking which drones are
    currently present.

    Attributes:
        name: Unique identifier used in map files and output lines.
        x: Integer grid X coordinate as parsed from the map file.
        y: Integer grid Y coordinate as parsed from the map file.
        zone: Zone type string — one of ``'normal'``, ``'blocked'``,
            ``'restricted'``, or ``'priority'``.
        max_drones: Maximum drones allowed simultaneously; defaults to
            ``1``.  Start and end zones are set to ``nb_drones`` so they
            can hold the entire fleet.
        color: CSS colour name used for rendering; ``'none'`` when unset.
        is_start: ``True`` for the unique ``start_hub`` zone.
        is_end: ``True`` for the unique ``end_hub`` zone.
        cost: Pathfinding weight for entering this zone.  ``1.0`` for
            normal/priority zones (priority uses ``0.2`` so Dijkstra
            prefers it), ``2.0`` for restricted zones, effectively
            infinite for blocked zones (which are never enqueued).
        reserved: ``1`` when the zone is at capacity or locked because an
            incoming restricted-zone transit is committed, blocking further
            arrivals this turn; ``0`` otherwise.
        occupancy: Live list of drones currently inside the zone.
    """

    def __init__(self, name: str, x: int, y: int) -> None:
        """Creates a new Zone with default attributes.

        Args:
            name: The unique name of this zone as defined in the map file.
            x: Integer grid X coordinate.
            y: Integer grid Y coordinate.
        """
        self.name = name
        self.x = x
        self.y = y
        self.zone: str = 'normal'
        self.max_drones: int = 1
        self.color: str = 'none'
        self.is_start: bool = False
        self.is_end: bool = False
        self.cost: float = 1.0
        self.reserved: int = 0
        from drone import Drone
        self.occupancy: list['Drone'] = []

    def __repr__(self) -> str:
        """Returns the zone name, used in output lines and debug output.

        Returns:
            The zone's :attr:`name` string.
        """
        return self.name
