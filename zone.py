class Zone:
    def __init__(self, name: str, x: int, y: int) -> None:
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
        self.occupancy: list[Drone] = []

    def __repr__(self) -> str:
        return self.name
    



