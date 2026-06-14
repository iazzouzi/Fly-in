from zone import Zone

class Drone:
    def __init__(self, id: int, path: list[Zone], position: Zone) -> None:
        self.id = id
        self.x = 0
        self.y = 0
        self.path = path
        self.position = position
        self.delivered: int = 0

    def __repr__(self):
        return f"{self.id}"
