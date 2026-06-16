from graph import Graph
from drone import Drone
from zone import Zone
from time import sleep
from math import sqrt
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
        super().__init__(WIDTH, HIGHT, 'Fly-in')
        arcade.set_background_color(arcade.color.WHITE)
        self.graph = GRAPH
        self.turns = TURNS
        self.counter = 0
        self.play = False
        self.restart = False
        self.turn = self.turns[self.counter]
        self.camera = arcade.Camera2D()
        self.gui_camera = arcade.Camera2D()
        self.camera.zoom = 0.3

        self.labels:list[arcade.Text] = []
        for hub in self.graph.hubs.values():
            x = hub.x*300
            y = hub.y*600-90
            if hub.is_start or hub.is_end:
                self.labels.append(arcade.Text(hub.name, x, y, COLOR[hub.color], 36, anchor_x= "center", anchor_y="top", bold=True))
            else:
                self.labels.append(arcade.Text(hub.name, x, y, COLOR[hub.color], 36, anchor_x= "center", anchor_y="top", bold=True, rotation=13))

    def on_update(self, delta_time):
        if self.counter == len(self.turns):
            self.play = False
            self.counter = 0
            self.turn = self.turns[self.counter]
            sleep(1)
            for drone in self.graph.drones:
                drone.x = self.graph.start_hub.x
                drone.y = self.graph.start_hub.y

        if self.play:
            arrived = True
            for mv in self.turn:
                for drone in mv['drones']:
                    if mv['cost2']:
                        x1 = mv['from'].x
                        if mv['to'].x == x1:
                            x2 = mv['to'].x
                        else:
                            x2 = (mv['to'].x+x1)/2
                        y1 = mv['from'].y
                        if mv['to'].y == y1:
                            y2 = mv['to'].y
                        else:
                            y2 = (mv['to'].y+y1)/2
                    elif mv['f']:
                        x2 = mv['to'].x
                        if mv['from'].x == x2:
                            x1 = mv['from'].x
                        else:
                            x1 = (x2+mv['from'].x)/2
                        y2 = mv['to'].y
                        if mv['from'].y == y2:
                            y1 = mv['from'].y
                        else:
                            y1 = (y2+mv['from'].y)/2
                    else:
                        x1 = mv['from'].x
                        x2 = mv['to'].x
                        y1 = mv['from'].y
                        y2 = mv['to'].y

                    distance = sqrt((x2-x1)**2+(y2-y1)**2)
                    dx = x2 - drone.x
                    dy = y2 - drone.y
                    remain = sqrt(dx**2+dy**2)

                    if remain < 0.1:
                        drone.x = x2
                        drone.y = y2
                    else:
                        drone.x += (dx/remain)*delta_time*distance
                        drone.y += (dy/remain)*delta_time*distance
                        arrived = False

            if arrived:
                self.counter += 1
                if self.counter < len(self.turns):
                    self.turn = self.turns[self.counter] 
            
        if self.restart:
            self.counter = 0
            self.turn = self.turns[self.counter]
            for drone in self.graph.drones:
                drone.x = self.graph.start_hub.x
                drone.y = self.graph.start_hub.y


    def on_draw(self):
        self.clear()
        self.camera.use()

        for conn in self.graph.connections:
            arcade.draw_line(conn.from_zone.x*300, conn.from_zone.y*600, conn.to_zone.x*300, conn.to_zone.y*600, COLOR['black'], 6)

        for hub in self.graph.hubs.values():
            arcade.draw_circle_filled(hub.x*300, hub.y*600, 90, arcade.color.WHITE)
            arcade.draw_circle_outline(hub.x*300, hub.y*600, 90, COLOR[hub.color], 20)

        for label in self.labels:
            label.draw()

        for drone in self.graph.drones:
            arcade.draw_sprite(arcade.Sprite('drone.png', 0.6, drone.x*300, drone.y*600))
            arcade.Text(str(drone.id), drone.x*300, drone.y*600, (0x3d, 0x66, 0x85), anchor_x= "center", anchor_y="center", font_size=26, bold=True).draw()

        self.gui_camera.use()

        arcade.Text(f"Turns: {self.counter}/{len(self.turns)}", 20, self.height - 20, (0x3d, 0x66, 0x85), 29, anchor_y="top", bold=True).draw()

        if self.play:
            arcade.draw_sprite(arcade.Sprite('space.png', 0.27, 90, 60))
        else:
            arcade.draw_sprite(arcade.Sprite('space.png', 0.3, 90, 60))
        
        if self.restart:
            arcade.draw_sprite(arcade.Sprite('tab.png', 0.2, 260, 60))
            self.restart = False
        else:
            arcade.draw_sprite(arcade.Sprite('tab.png', 0.23, 260, 60))

    def on_mouse_scroll(self, x: float, y: float, scroll_x: float, scroll_y: float):
        if scroll_y > 0:
            self.camera.zoom *= 1.1
        else:
            self.camera.zoom *= 0.9


    def on_mouse_drag(self, x: int, y: int, dx: int, dy: int, buttons: int, modifiers: int):
        if buttons & arcade.MOUSE_BUTTON_LEFT:
            pos = self.camera.position
            self.camera.position = (pos.x - (dx/self.camera.zoom), pos.y - (dy/self.camera.zoom))


    def on_key_press(self, key, modifiers):
        if key == arcade.key.SPACE:
            if self.play:
                self.play = False
            else:
                self.play = True
        elif key == arcade.key.TAB:
            self.restart = True

class Visualizer:
    @staticmethod
    def run(WIDTH: int, HIGHT: int, GRAPH: Graph, TURNS: list):
        Window(WIDTH, HIGHT, GRAPH, TURNS)
        arcade.run()