from zone import Zone


class Drone:
    """A single autonomous drone participating in the simulation.

    The ``x`` and ``y`` attributes are floating-point screen coordinates
    used by the visualizer for smooth interpolation; they are distinct from
    the integer grid coordinates stored on :class:`~zone.Zone`.

    Attributes:
        id: Unique 1-based numeric identifier assigned at spawn time.
        x: Visualizer X position, interpolated continuously between zone
            centres during animation.
        y: Visualizer Y position, interpolated continuously between zone
            centres during animation.
        path: Ordered list of every :class:`~zone.Zone` the drone has
            occupied, starting from the ``start_hub``.  Appended to by the
            engine each time the drone enters a new zone and used to
            calculate cumulative path cost.
        position: The zone the drone currently occupies in the simulation
            state (may differ from the visual position mid-animation).
        delivered: ``1`` once the drone has reached the ``end_hub``,
            ``0`` otherwise.  Used by the engine to count remaining drones.
    """

    def __init__(self, id: int, path: list[Zone], position: Zone) -> None:
        """Spawns a new Drone at the given position.

        Args:
            id: Unique numeric identifier for this drone.
            path: Initial path list, typically ``[]`` on creation; the
                engine appends the starting zone immediately after spawning.
            position: The zone where the drone begins the simulation.
        """
        self.id = id
        self.x: float = 0.0
        self.y: float = 0.0
        self.path = path
        self.position = position
        self.delivered: int = 0

    def __repr__(self) -> str:
        """Returns the drone's numeric ID as a string.

        Returns:
            The string form of :attr:`id`, e.g. ``'3'``.
        """
        return f"{self.id}"
