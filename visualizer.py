import arcade
from models.graph import Graph
from models.drone import Drone
from models.zone import Zone

COLOR_MAP = {
    'red': arcade.color.RED,
    'green': arcade.color.APPLE_GREEN,
    'blue': arcade.color.BLUE_SAPPHIRE,
    'yellow': arcade.color.GOLD,
    'gray': arcade.color.GRAY,
    'none': arcade.color.LIGHT_GRAY,
}


class Window(arcade.Window):
    def __init__(self, WIDTH: int, HIGHT: int, GRAPH: Graph, TURNS: list[list[dict[str, list[Drone] | Zone | int]]]):
        super().__init__(WIDTH, HIGHT, 'Fly-in')
        self.graph = GRAPH
        self.turns = TURNS

class Visualizer:
    @staticmethod
    def run(WIDTH: int, HIGHT: int, GRAPH: Graph, TURNS: list):
        window = Window(WIDTH, HIGHT, GRAPH, TURNS)
        arcade.run()