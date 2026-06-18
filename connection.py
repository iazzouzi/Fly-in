from zone import Zone


class Connection:
    """Represents a bidirectional edge connecting two zones in the network.

    Attributes:
        from_zone (Zone): The primary node of the connection.
        to_zone (Zone): The secondary node of the connection.
        max_link_capacity (int): Maximum number of drones that can
            simultaneously travel across this link.
    """

    def __init__(
        self, from_zone: Zone, to_zone: Zone, max_link_capacity: int
    ) -> None:
        """Initializes a new Connection instance.

        Args:
            from_zone (Zone): The starting zone of the link.
            to_zone (Zone): The destination zone of the link.
            max_link_capacity (int): Capacity limit for concurrent drone
                traversal.
        """
        self.from_zone = from_zone
        self.to_zone = to_zone
        self.max_link_capacity = max_link_capacity
