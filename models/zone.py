class Zone:
    def __init__(self, name, x, y):
        self.name: str = name
        self.x: int = x
        self.y: int = y
        self.zone: str = 'normal'
        self.max_drones: int = 1
        self.color: str = 'none'
        self.is_start: bool = False
        self.is_end: bool = False
        self.cost: int = 1
        self.reserved = False

    def __str__(self):
        return self.name
    



