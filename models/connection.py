from .zone import Zone
class Connection:
    def __init__(self, from_zone, to_zone, max_link_capacity):
        self.from_zone: Zone = from_zone
        self.to_zone: Zone = to_zone
        self.max_link_capacity: int = max_link_capacity