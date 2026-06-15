from graph import Graph
from drone import Drone
from zone import Zone
from arcade.gui import UIManager, UILabel
import arcade

COLOR = {
    'red': arcade.color.RED,
    'purple': arcade.color.PURPLE,
    'black': arcade.color.BLACK,
    'brown': arcade.color.BROWN,
    'orange': arcade.color.ORANGE,
    'maroon': arcade.color.MAROON,
    'gold': arcade.color.GOLD,
    'darkred': arcade.color.DARK_RED,
    'violet': arcade.color.VIOLET,
    'crimson': arcade.color.CRIMSON,
    'rainbow': arcade.color.GOLD_FUSION,
    'blue': arcade.color.BLUE_SAPPHIRE,
    'yellow': arcade.color.GOLD,
    'green': arcade.color.APPLE_GREEN,
    'cyan': arcade.color.CYAN,
    'lime': arcade.color.LIME,
    'magenta': arcade.color.MAGENTA,
    'gray': arcade.color.GRAY,
    'none': arcade.color.LIGHT_GRAY,
}
class Window(arcade.Window):
    def __init__(self, WIDTH: int, HIGHT: int, GRAPH: Graph, TURNS: list[list[dict[str, list[Drone] | Zone | int]]]):
        super().__init__(WIDTH, HIGHT, 'Fly-in', resizable=True)
        arcade.set_background_color(arcade.color.WHITE)
        self.graph = GRAPH
        self.turns = TURNS
        self.counter = 0
        self.play = False
        self.turn = self.turns[self.counter]
        self.camera = arcade.Camera2D()
        self.manager = UIManager()
        self.manager.enable()
        self.labels:list[arcade.Text] = []
        for hub in self.graph.hubs.values():
            x = hub.x*300
            y = hub.y*600-90
            if hub.is_start or hub.is_end:
                self.labels.append(arcade.Text(hub.name, x, y, COLOR[hub.color], 36, anchor_x= "center", anchor_y="top", bold=True))
            else:
                self.labels.append(arcade.Text(hub.name, x, y, COLOR[hub.color], 36, anchor_x= "center", anchor_y="top", bold=True, rotation=13))
        for drone in self.graph.drones:
            drone.x = self.graph.start_hub.x
            drone.y = self.graph.start_hub.y

    def turn_nb(self):
        return arcade.Text(f"Turns: {self.counter}/{len(self.turns)}", 0, 1900, COLOR['black'], 160, bold=True)
    
    @staticmethod
    def drone_nb(drone: Drone) -> arcade.Text:
        return arcade.Text(str(drone.id), drone.x*300, drone.y*600, COLOR['black'], anchor_x= "center", anchor_y="center", font_size=26, bold=True)

    def on_update(self, delta_time):

        if self.counter == len(self.turns):
            self.play = False
            self.counter = 0
            self.turn = self.turns[self.counter]
            for drone in self.graph.drones:
                drone.x = self.graph.start_hub.x
                drone.y = self.graph.start_hub.y

    def on_draw(self):
        self.clear()
        self.camera.use()
        self.turn_nb().draw()

        for conn in self.graph.connections:
            arcade.draw_line(conn.from_zone.x*300, conn.from_zone.y*600, conn.to_zone.x*300, conn.to_zone.y*600, COLOR['black'], 6)

        for hub in self.graph.hubs.values():
            arcade.draw_circle_filled(hub.x*300, hub.y*600, 90, arcade.color.WHITE)
            arcade.draw_circle_outline(hub.x*300, hub.y*600, 90, COLOR[hub.color], 20)

        for label in self.labels:
            label.draw()

        for drone in self.graph.drones:
            arcade.draw_circle_filled(drone.x*300, drone.y*600, 30, COLOR['gold'])
            self.drone_nb(drone).draw()

    def on_resize(self, width: float, height: float):
        super().on_resize(width, height)
        self.camera.equalise()


    def on_mouse_scroll(self, x: int, y: int, scroll_x: int, scroll_y: int):
        if scroll_y > 0:
            self.camera.zoom *= 1.1
        else:
            self.camera.zoom *= 0.9


    def on_mouse_drag(self, x: int, y: int, dx: int, dy: int, buttons: int, modifiers: int):
        if buttons & arcade.MOUSE_BUTTON_LEFT:
            pos = self.camera.position
            self.camera.position = (pos.x - (dx/self.camera.zoom), pos.y - (dy/self.camera.zoom))


    def on_key_press(self, key, modifiers):
        if arcade.key.SPACE:
            if self.play:
                self.play = False
            else:
                self.play = True

class Visualizer:
    @staticmethod
    def run(WIDTH: int, HIGHT: int, GRAPH: Graph, TURNS: list):
        Window(WIDTH, HIGHT, GRAPH, TURNS)
        arcade.run()