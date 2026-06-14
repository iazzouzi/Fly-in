from zone import Zone
class Connection:
    def __init__(self, from_zone: Zone, to_zone: Zone, max_link_capacity: int) -> None:
        self.from_zone = from_zone
        self.to_zone = to_zone
        self.max_link_capacity = max_link_capacity