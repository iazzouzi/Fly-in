from .zone import Zone

class Drone:
    def __init__(self, id, position):
        self.id: int = id
        self.position: Zone = position

    def __str__(self):
        return self.id
