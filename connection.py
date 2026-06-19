from zone import Zone


class Connection:
    """A bidirectional edge linking two zones in the routing network.

    Connections are undirected: the engine checks both orderings when
    resolving adjacency.  The ``max_link_capacity`` attribute limits how
    many drones may traverse the link in the same simulation turn,
    independently of the zone capacity constraints at either endpoint.

    Attributes:
        from_zone: One endpoint of the connection (the zone named first
            in the ``connection: A-B`` map line).
        to_zone: The other endpoint of the connection.
        max_link_capacity: Maximum number of drones that may simultaneously
            travel across this link in a single turn.  Defaults to ``1``.
    """

    def __init__(
        self, from_zone: Zone, to_zone: Zone, max_link_capacity: int
    ) -> None:
        """Creates a bidirectional connection between two zones.

        Args:
            from_zone: The zone named on the left side of ``A-B``.
            to_zone: The zone named on the right side of ``A-B``.
            max_link_capacity: Maximum simultaneous drone traversals per
                turn on this link.
        """
        self.from_zone = from_zone
        self.to_zone = to_zone
        self.max_link_capacity = max_link_capacity
