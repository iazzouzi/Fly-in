from .zone import Zone

class Drone:
    def __init__(self, id, path, position):
        self.id: int = id
        self.path: list[str] = path
        self.position: Zone = position
