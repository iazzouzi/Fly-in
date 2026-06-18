from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from drone import Drone


class Zone:
    """Represents a discrete zone (node) in the drone routing network.

    Attributes:
        name (str): Unique identifier for the zone.
        x (int): X coordinate of the zone.
        y (int): Y coordinate of the zone.
        zone (str): Type of zone ('normal', 'blocked', 'restricted',
            'priority').
        max_drones (int): Maximum number of drones that can simultaneously
            occupy this zone.
        color (str): Color name for visual representation.
        is_start (bool): True if this is the starting zone.
        is_end (bool): True if this is the destination zone.
        cost (float): Movement cost to reach this zone (1.0 for normal,
            2.0 for restricted, 0.2 for priority).
        reserved (int): Number of incoming drones reserved for capacity
            management.
        occupancy (list[Drone]): List of drones currently residing in the
            zone.
    """

    def __init__(self, name: str, x: int, y: int) -> None:
        """Initializes a new Zone instance.

        Args:
            name (str): The unique name of the zone.
            x (int): The X coordinate.
            y (int): The Y coordinate.
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
        self.occupancy: list['Drone'] = []

    def __repr__(self) -> str:
        """Returns the string representation of the zone.

        Returns:
            str: The name of the zone.
        """
        return self.name
