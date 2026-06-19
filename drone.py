from zone import Zone


class Drone:
    """Represents a single autonomous drone within the simulation.

    Attributes:
        id (int): Unique numeric identifier for the drone.
        x (float): Current X coordinate position in the visualization.
        y (float): Current Y coordinate position in the visualization.
        path (list[Zone]): Chronological history of zones the drone has
            visited, appended to incrementally as the drone moves.
            Starts empty and is used by the engine to calculate
            cumulative path cost.
        position (Zone): The current zone the drone is occupying.
        delivered (int): Status flag indicating if the drone has reached
            the end hub.
    """

    def __init__(self, id: int, path: list[Zone], position: Zone) -> None:
        """Initializes a new Drone instance.

        Args:
            id (int): Unique identifier for the drone.
            path (list[Zone]): Initial assigned path for the drone.
            position (Zone): The starting zone for the drone.
        """
        self.id = id
        self.x = 0.0
        self.y = 0.0
        self.path = path
        self.position = position
        self.delivered: int = 0

    def __repr__(self) -> str:
        """Returns the string representation of the drone.

        Returns:
            str: The unique ID of the drone.
        """
        return f"{self.id}"
