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
        self.camera = arcade.Camera2D()
        self.manager = UIManager()
        self.manager.add(UILabel(text=f"Turns: {self.counter}", x=20, y=self.height-60, bold=True, text_color=COLOR['black'], font_size=30))
        self.manager.enable()
        self.labels:list[arcade.Text] = []
        # self.drones_id = []
        # for i in range(1, self.nb_drones+1):
        #     self.drones_id.append(arcade.Text(str(i), drone.x*300, drone.y*300, COLOR['black'], anchor_x= "center", anchor_y="center", font_size=26, bold=True))

        self.gen_labels()

    def gen_labels(self):
        for hub in self.graph.hubs.values():
            x = hub.x*300
            if hub.name in {'conv_restricted2', 'conv_restricted5', 'conv_restricted8', 'priority_correct', 'priority_bypass2', 'restricted_tunnel2'}:
                y = hub.y*600-130
            else:
                y = hub.y*600+90
            self.labels.append(arcade.Text(hub.name, x, y, COLOR[hub.color], anchor_x= "center", anchor_y="bottom", font_size=26, bold=True))


    def on_update(self, delta_time):
        pass


    def on_draw(self):
        self.clear()
        self.camera.use()
        self.manager.draw()

        for conn in self.graph.connections:
            arcade.draw_line(conn.from_zone.x*300, conn.from_zone.y*600, conn.to_zone.x*300, conn.to_zone.y*600, COLOR['black'], 6)

        for hub in self.graph.hubs.values():
            arcade.draw_circle_filled(hub.x*300, hub.y*600, 90, arcade.color.WHITE)
            arcade.draw_circle_outline(hub.x*300, hub.y*600, 90, COLOR[hub.color], 20)

        for label in self.labels:
            label.draw()

        # if self.play:
        #     for turn in self.turns:
        #         for mv in turn:
        #             for drone in mv['drones']:
        #                 arcade.draw_circle_filled(x*300, y*600, 30, COLOR['gold'])
        #                 arcade.draw_text(str(drone.id), drone.x*300, drone.y*300, COLOR['black'], anchor_x= "center", anchor_y="center", font_size=26, bold=True)

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
            self.play = True

class Visualizer:
    @staticmethod
    def run(WIDTH: int, HIGHT: int, GRAPH: Graph, TURNS: list):
        Window(WIDTH, HIGHT, GRAPH, TURNS)
        arcade.run()