class Zone:
    def __init__(self, name, x, y, zone, max_drones, color):
        self.name = name
        self.x = x
        self.y = y
        self.zone = zone
        self.max_drones = max_drones
        self.color = color

    def __str__(self):
        return self.name
    



