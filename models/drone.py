from .zone import Zone

class Drone:
    def __init__(self, id: int, path: list[str], position: Zone | None) -> None:
        self.id = id
        self.path = path
        self.position = position
        self.delivered: int = 0

    def __repr__(self):
        return f"{self.id}"
