from graph import Graph
from drone import Drone
from zone import Zone
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
    def __init__(self, WIDTH: int, HEIGHT: int, GRAPH: Graph, TURNS: list[list[dict[str, list[Drone] | Zone | int]]]):
        super().__init__(WIDTH, HEIGHT, 'Fly-in', resizable=True)
        arcade.set_background_color(arcade.color.OXFORD_BLUE)
        self.graph = GRAPH
        self.turns = TURNS
        self.counter = 0
        self.play = False
        self.restart = False
        self.sound = arcade.load_sound('Sound.mp3')
        self.player = None
        self.play_sound = False
        self.next = False
        self.space1 = arcade.Sprite('space.png', 0.27, 90, 60)
        self.space2 = arcade.Sprite('space.png', 0.3, 90, 60)
        self.r1 = arcade.Sprite('r.png', 0.19, 300, 60)
        self.r2 = arcade.Sprite('r.png', 0.22, 300, 60)
        self.tab1 = arcade.Sprite('tab.png', 0.27, 490, 60)
        self.tab2 = arcade.Sprite('tab.png', 0.24, 490, 60)
        self.right1 = arcade.Sprite('right.png', 0.19, 680, 60)
        self.right2 = arcade.Sprite('right.png', 0.22, 680, 60)

        self.drone = arcade.Sprite('drone.png', 0.6, 0, 0)
        self.turn = self.turns[self.counter]
        self.camera = arcade.Camera2D()
        self.gui_camera = arcade.Camera2D()
        self.camera.zoom = 0.26
        self.camera.position = (self.width+self.width/1.26, 0)

        self.labels:list[arcade.Text] = []
        for hub in self.graph.hubs.values():
            x = hub.x*300
            y = hub.y*600-90
            if hub.is_start or hub.is_end:
                self.labels.append(arcade.Text(hub.name, x+1, y, COLOR[hub.color], 36, anchor_x= "center", anchor_y="top", bold=True))
                self.labels.append(arcade.Text(hub.name, x-1, y, COLOR[hub.color], 36, anchor_x= "center", anchor_y="top", bold=True))
                self.labels.append(arcade.Text(hub.name, x, y+1, COLOR[hub.color], 36, anchor_x= "center", anchor_y="top", bold=True))
                self.labels.append(arcade.Text(hub.name, x, y-1, COLOR[hub.color], 36, anchor_x= "center", anchor_y="top", bold=True))
                self.labels.append(arcade.Text(hub.name, x, y, COLOR[hub.color], 36, anchor_x= "center", anchor_y="top", bold=True))


            else:
                self.labels.append(arcade.Text(hub.name, x+1, y, COLOR[hub.color], 36, anchor_x= "center", anchor_y="top", bold=True, rotation=13))
                self.labels.append(arcade.Text(hub.name, x-1, y, COLOR[hub.color], 36, anchor_x= "center", anchor_y="top", bold=True, rotation=13))
                self.labels.append(arcade.Text(hub.name, x, y+1, COLOR[hub.color], 36, anchor_x= "center", anchor_y="top", bold=True, rotation=13))
                self.labels.append(arcade.Text(hub.name, x, y-1, COLOR[hub.color], 36, anchor_x= "center", anchor_y="top", bold=True, rotation=13))
                self.labels.append(arcade.Text(hub.name, x, y, COLOR[hub.color], 36, anchor_x= "center", anchor_y="top", bold=True, rotation=13))


        self.dronenb: list[arcade.Text] = [
            arcade.Text('', 0, 0, arcade.color.OXFORD_BLUE, 26, anchor_x= "center", anchor_y="center", bold=True),
            arcade.Text('', 0, 0, arcade.color.OXFORD_BLUE, 26, anchor_x= "center", anchor_y="center", bold=True),
            arcade.Text('', 0, 0, arcade.color.OXFORD_BLUE, 26, anchor_x= "center", anchor_y="center", bold=True),
            arcade.Text('', 0, 0, arcade.color.OXFORD_BLUE, 26, anchor_x= "center", anchor_y="center", bold=True),
            arcade.Text('', 0, 0, arcade.color.BLUE_SAPPHIRE, 26, anchor_x= "center", anchor_y="center", bold=True)
        ]

        self.gui_texts: list[arcade.Text] = [
            arcade.Text(f"Turns: {self.counter}/{len(self.turns)}", 17, self.height - 20, arcade.color.WHITE, 28, anchor_y="top", bold=True),
            arcade.Text(f"Turns: {self.counter}/{len(self.turns)}", 23, self.height - 20, arcade.color.WHITE, 28, anchor_y="top", bold=True),
            arcade.Text(f"Turns: {self.counter}/{len(self.turns)}", 20, self.height - 17, arcade.color.WHITE, 28, anchor_y="top", bold=True),
            arcade.Text(f"Turns: {self.counter}/{len(self.turns)}", 20, self.height - 23, arcade.color.WHITE, 28, anchor_y="top", bold=True),
            arcade.Text(f"Turns: {self.counter}/{len(self.turns)}", 20, self.height - 20, arcade.color.BLUE_SAPPHIRE, 28, anchor_y="top", bold=True),
            arcade.Text(f"Drones: {self.graph.nb_drones}", 17, self.height - 70, arcade.color.WHITE, 24, anchor_y="top", bold=True),
            arcade.Text(f"Drones: {self.graph.nb_drones}", 23, self.height - 70, arcade.color.WHITE, 24, anchor_y="top", bold=True),
            arcade.Text(f"Drones: {self.graph.nb_drones}", 20, self.height - 67, arcade.color.WHITE, 24, anchor_y="top", bold=True),
            arcade.Text(f"Drones: {self.graph.nb_drones}", 20, self.height - 73, arcade.color.WHITE, 24, anchor_y="top", bold=True),
            arcade.Text(f"Drones: {self.graph.nb_drones}", 20, self.height - 70, arcade.color.BLUE_SAPPHIRE, 24, anchor_y="top", bold=True),
            arcade.Text(f"Zoom: x{round(self.camera.zoom, 2)}", 17, self.height - 120, arcade.color.WHITE, 20, anchor_y="top", bold=True),
            arcade.Text(f"Zoom: x{round(self.camera.zoom, 2)}", 23, self.height - 120, arcade.color.WHITE, 20, anchor_y="top", bold=True),
            arcade.Text(f"Zoom: x{round(self.camera.zoom, 2)}", 20, self.height - 117, arcade.color.WHITE, 20, anchor_y="top", bold=True),
            arcade.Text(f"Zoom: x{round(self.camera.zoom, 2)}", 20, self.height - 123, arcade.color.WHITE, 20, anchor_y="top", bold=True),
            arcade.Text(f"Zoom: x{round(self.camera.zoom, 2)}", 20, self.height - 120, arcade.color.BLUE_SAPPHIRE, 20, anchor_y="top", bold=True),
            arcade.Text("<Pause>" if self.play else "<Start>", 26, 120, arcade.color.WHITE, 23, bold=True),
            arcade.Text("<Pause>" if self.play else "<Start>", 20, 120, arcade.color.WHITE, 23, bold=True),
            arcade.Text("<Pause>" if self.play else "<Start>", 23, 123, arcade.color.WHITE, 23, bold=True),
            arcade.Text("<Pause>" if self.play else "<Start>", 23, 117, arcade.color.WHITE, 23, bold=True),
            arcade.Text("<Pause>" if self.play else "<Start>", 23, 120, arcade.color.BLUE_SAPPHIRE, 23, bold=True),
            arcade.Text('<Restart>', 229, 110, arcade.color.WHITE, 19, bold=True),
            arcade.Text('<Restart>', 223, 110, arcade.color.WHITE, 19, bold=True),
            arcade.Text('<Restart>', 226, 113, arcade.color.WHITE, 19, bold=True),
            arcade.Text('<Restart>', 226, 107, arcade.color.WHITE, 19, bold=True),
            arcade.Text('<Restart>', 226, 110, arcade.color.BLUE_SAPPHIRE, 19, bold=True),
            arcade.Text('<Sound>', 423, 110, arcade.color.WHITE, 21, bold=True),
            arcade.Text('<Sound>', 417, 110, arcade.color.WHITE, 21, bold=True),
            arcade.Text('<Sound>', 420, 113, arcade.color.WHITE, 21, bold=True),
            arcade.Text('<Sound>', 420, 107, arcade.color.WHITE, 21, bold=True),
            arcade.Text('<Sound>', 420, 110, arcade.color.BLUE_SAPPHIRE, 21, bold=True),
            arcade.Text('<Next turn>', 600, 110, arcade.color.WHITE, 17, bold=True),
            arcade.Text('<Next turn>', 594, 110, arcade.color.WHITE, 17, bold=True),
            arcade.Text('<Next turn>', 597, 113, arcade.color.WHITE, 17, bold=True),
            arcade.Text('<Next turn>', 597, 107, arcade.color.WHITE, 17, bold=True),
            arcade.Text('<Next turn>', 597, 110, arcade.color.BLUE_SAPPHIRE, 17, bold=True)]

    def on_update(self, delta_time):

        if self.counter == len(self.turns):
            if self.player:
                arcade.stop_sound(self.player)
                self.player = None
            self.play = False
            self.counter = 0
            self.turn = self.turns[self.counter]
            for drone in self.graph.drones:
                drone.x = self.graph.start_hub.x
                drone.y = self.graph.start_hub.y

        if self.play or self.next:
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
                self.next = False
            
        if self.restart:
            self.play = False
            self.counter = 0
            self.turn = self.turns[self.counter]
            for drone in self.graph.drones:
                drone.x = self.graph.start_hub.x
                drone.y = self.graph.start_hub.y

        if self.play_sound and self.player and not arcade.Sound.is_playing(self.sound, self.player):
            self.player = arcade.play_sound(self.sound)

        if not self.play_sound:
            if self.player:
                arcade.stop_sound(self.player)


        for i in range(5):
            self.gui_texts[i].text = f"Turns: {self.counter}/{len(self.turns)}"

        self.gui_texts[0].y = self.height - 20
        self.gui_texts[1].y = self.height - 20
        self.gui_texts[2].y = self.height - 17
        self.gui_texts[3].y = self.height - 23
        self.gui_texts[4].y = self.height - 20
        self.gui_texts[5].y = self.height - 70
        self.gui_texts[6].y = self.height - 70
        self.gui_texts[7].y = self.height - 67
        self.gui_texts[8].y = self.height - 73
        self.gui_texts[9].y = self.height - 70
        self.gui_texts[10].y = self.height - 120
        self.gui_texts[11].y = self.height - 120
        self.gui_texts[12].y = self.height - 117
        self.gui_texts[13].y = self.height - 123
        self.gui_texts[14].y = self.height - 120



        for i in range(10, 15):
            self.gui_texts[i].text = f"Zoom: x{round(self.camera.zoom, 2)}"

        for i in range(15, 20):
            self.gui_texts[i].text = "<Pause>" if self.play else "<Start>"

    def on_draw(self):

        self.clear()
        self.camera.use()


        for conn in self.graph.connections:
            arcade.draw_line(conn.from_zone.x*300, conn.from_zone.y*600, conn.to_zone.x*300, conn.to_zone.y*600, COLOR['black'], 6)

        for hub in self.graph.hubs.values():
            radius = 90
            arcade.draw_circle_filled(hub.x*300, hub.y*600, radius, arcade.color.WHITE_SMOKE)
            arcade.draw_circle_outline(hub.x*300, hub.y*600, radius, COLOR[hub.color], 60)

        for label in self.labels:
            label.draw()

        for drone in self.graph.drones:
            self.drone.center_x = drone.x*300
            self.drone.center_y = drone.y*600
            arcade.draw_sprite(self.drone)

            for txt in self.dronenb:
                txt.text = str(drone.id)
                self.dronenb[0].x = (drone.x+0.029)*300
                self.dronenb[0].y = (drone.y+0.026)*600
                self.dronenb[1].x = (drone.x+0.023)*300
                self.dronenb[1].y = (drone.y+0.026)*600
                self.dronenb[2].x = (drone.x+0.026)*300
                self.dronenb[2].y = (drone.y+0.029)*600
                self.dronenb[3].x = (drone.x+0.026)*300
                self.dronenb[3].y = (drone.y+0.023)*600
                self.dronenb[4].x = (drone.x+0.026)*300
                self.dronenb[4].y = (drone.y+0.026)*600

            for txt in self.dronenb:
                txt.draw()

        self.gui_camera.use()

        for text in self.gui_texts:
            text.draw()

        if self.play:
            arcade.draw_sprite(self.space1)
        else:
            arcade.draw_sprite(self.space2)

        if self.restart:
            arcade.draw_sprite(self.r1)
            self.restart = False
        else:
            arcade.draw_sprite(self.r2)

        if self.play_sound:
            arcade.draw_sprite(self.tab1)
        else:
            arcade.draw_sprite(self.tab2)

        if self.next:
            arcade.draw_sprite(self.right1)
        else:
            arcade.draw_sprite(self.right2)

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
                if self.player:
                    arcade.stop_sound(self.player)
                    self.player = None
            else:
                if self.play_sound:
                    self.player = arcade.play_sound(self.sound)
                self.play = True

        elif key == arcade.key.R:
            if self.player:
                arcade.stop_sound(self.player)
                self.player = None
            self.restart = True

        elif key == arcade.key.TAB:
            if self.play_sound:
                self.play_sound = False
            elif not self.play_sound:
                self.play_sound = True

        elif key == arcade.key.RIGHT:
            self.next = True
class Visualizer:
    @staticmethod
    def run(WIDTH: int, HIGHT: int, GRAPH: Graph, TURNS: list):
        Window(WIDTH, HIGHT, GRAPH, TURNS)
        arcade.run()