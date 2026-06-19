from graph import Graph
from drone import Drone
from zone import Zone
from math import sqrt
import arcade
import webcolors  # type: ignore[import-untyped]
from pyglet.media.player import Player


class Window(arcade.Window):
    """Arcade window that animates the drone routing simulation.

    Renders the network graph as coloured circles (zones) joined by lines
    (connections), overlays a drone sprite that moves smoothly between
    zone centres, and provides interactive playback controls via keyboard
    and mouse.

    Attributes:
        graph: The parsed routing network, used to read zone positions,
            colours, and the full drone list.
        turns: Complete movement timeline produced by the engine; each
            entry is a list of movement dicts for one simulation turn.
        counter: Index of the turn currently being rendered (0-based).
        play: ``True`` while the simulation is auto-advancing frame by
            frame.
        restart: ``True`` for one frame when the user triggers a restart;
            resets all drone positions to the start hub.
        sound: Loaded background music asset.
        player: Active pyglet audio player, or ``None`` when silent.
        play_sound: ``True`` when background music is enabled.
        next: ``True`` for one turn when the user requests a single step
            forward while paused.
        space1: Play-button sprite (active/highlighted state).
        space2: Play-button sprite (inactive state).
        r1: Restart-button sprite (active state).
        r2: Restart-button sprite (inactive state).
        tab1: Sound-toggle sprite (active state).
        tab2: Sound-toggle sprite (inactive state).
        right1: Next-turn sprite (active state).
        right2: Next-turn sprite (inactive state).
        drone: Single reusable drone sprite repositioned each frame.
        turn: Movement dict list for the turn currently in progress.
        camera: Zoomable/pannable camera used to render the graph.
        gui_camera: Fixed camera used to render the HUD overlay.
        labels: Zone name text objects rendered above each node.
        dronenb: Five stacked text objects (4 outline + 1 fill) used to
            render each drone's ID with a drop-shadow effect.
        gui_texts: All HUD text objects (turn counter, drone count, zoom
            level, and button labels).
        TMP: Set of drones that have already arrived at the end hub and
            should be rendered only once rather than stacked.
    """

    def __init__(
        self,
        width: int,
        height: int,
        graph: Graph,
        turns: list[list[dict[str, list[Drone] | Zone | int]]],
    ) -> None:
        """Initialises the window, loads assets, and builds all UI elements.

        Args:
            width: Window width in pixels.
            height: Window height in pixels.
            graph: The fully parsed routing network.
            turns: The movement timeline returned by the engine.
        """
        super().__init__(width, height, 'Fly-in', resizable=True)
        arcade.set_background_color(arcade.color.OXFORD_BLUE)
        self.graph = graph
        self.turns = turns
        self.counter = 0
        self.play = False
        self.restart = False
        self.sound = arcade.load_sound('Sound.mp3')
        self.player: Player | None = None
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
        self.camera.position = (
            self.width + self.width / 1.26, 0
        )

        self.labels: list[arcade.Text] = []
        for hub in self.graph.hubs.values():
            if hub.color == 'none':
                hub.color = 'white'
            color = webcolors.name_to_rgb(hub.color)
            x = hub.x * 300
            y = hub.y * 600 - 90
            rotation = 0 if (hub.is_start or hub.is_end) else 13
            for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                self.labels.append(
                    arcade.Text(
                        hub.name,
                        x + dx,
                        y + dy,
                        color,
                        36,
                        anchor_x="center",
                        anchor_y="top",
                        bold=True,
                        rotation=rotation,
                    )
                )

        self.dronenb: list[arcade.Text] = []
        for i in range(4):
            self.dronenb.append(
                arcade.Text(
                    '',
                    0,
                    0,
                    arcade.color.OXFORD_BLUE,
                    26,
                    anchor_x="center",
                    anchor_y="center",
                    bold=True,
                )
            )
        self.dronenb.append(
            arcade.Text(
                '',
                0,
                0,
                arcade.color.BLUE_SAPPHIRE,
                26,
                anchor_x="center",
                anchor_y="center",
                bold=True,
            )
        )

        self.gui_texts: list[arcade.Text] = []

        for dx, dy in [(-3, 0), (+3, 0), (0, -3), (0, +3)]:
            self.gui_texts.append(
                arcade.Text(
                    f"Turns: {self.counter}/{len(self.turns)}",
                    20 + dx,
                    self.height - 20 + dy,
                    arcade.color.WHITE,
                    28,
                    anchor_y="top",
                    bold=True,
                )
            )
        self.gui_texts.append(
            arcade.Text(
                f"Turns: {self.counter}/{len(self.turns)}",
                20,
                self.height - 20,
                arcade.color.BLUE_SAPPHIRE,
                28,
                anchor_y="top",
                bold=True,
            )
        )

        for dx, dy in [(-3, 0), (+3, 0), (0, -3), (0, +3)]:
            self.gui_texts.append(
                arcade.Text(
                    f"Drones: {self.graph.nb_drones}",
                    20 + dx,
                    self.height - 70 + dy,
                    arcade.color.WHITE,
                    24,
                    anchor_y="top",
                    bold=True,
                )
            )
        self.gui_texts.append(
            arcade.Text(
                f"Drones: {self.graph.nb_drones}",
                20,
                self.height - 70,
                arcade.color.BLUE_SAPPHIRE,
                24,
                anchor_y="top",
                bold=True,
            )
        )

        for dx, dy in [(-3, 0), (+3, 0), (0, -3), (0, +3)]:
            self.gui_texts.append(
                arcade.Text(
                    f"Zoom: x{round(self.camera.zoom, 2)}",
                    20 + dx,
                    self.height - 120 + dy,
                    arcade.color.WHITE,
                    20,
                    anchor_y="top",
                    bold=True,
                )
            )
        self.gui_texts.append(
            arcade.Text(
                f"Zoom: x{round(self.camera.zoom, 2)}",
                20,
                self.height - 120,
                arcade.color.BLUE_SAPPHIRE,
                20,
                anchor_y="top",
                bold=True,
            )
        )

        for dx, dy in [(-3, 0), (+3, 0), (0, -3), (0, +3)]:
            msg = "<Pause>" if self.play else "<Start>"
            self.gui_texts.append(
                arcade.Text(
                    msg,
                    23 + dx,
                    120 + dy,
                    arcade.color.WHITE,
                    23,
                    bold=True,
                )
            )
        msg_status = "<Pause>" if self.play else "<Start>"
        self.gui_texts.append(
            arcade.Text(
                msg_status,
                23,
                120,
                arcade.color.BLUE_SAPPHIRE,
                23,
                bold=True,
            )
        )

        for dx, dy in [(-3, 0), (+3, 0), (0, -3), (0, +3)]:
            self.gui_texts.append(
                arcade.Text(
                    '<Restart>',
                    226 + dx,
                    110 + dy,
                    arcade.color.WHITE,
                    19,
                    bold=True,
                )
            )
        self.gui_texts.append(
            arcade.Text(
                '<Restart>',
                226,
                110,
                arcade.color.BLUE_SAPPHIRE,
                19,
                bold=True,
            )
        )

        for dx, dy in [(-3, 0), (+3, 0), (0, -3), (0, +3)]:
            self.gui_texts.append(
                arcade.Text(
                    '<Sound>',
                    420 + dx,
                    110 + dy,
                    arcade.color.WHITE,
                    21,
                    bold=True,
                )
            )
        self.gui_texts.append(
            arcade.Text(
                '<Sound>',
                420,
                110,
                arcade.color.BLUE_SAPPHIRE,
                21,
                bold=True,
            )
        )

        for dx, dy in [(-3, 0), (+3, 0), (0, -3), (0, +3)]:
            self.gui_texts.append(
                arcade.Text(
                    '<Next turn>',
                    597 + dx,
                    110 + dy,
                    arcade.color.WHITE,
                    17,
                    bold=True,
                )
            )
        self.gui_texts.append(
            arcade.Text(
                '<Next turn>',
                597,
                110,
                arcade.color.BLUE_SAPPHIRE,
                17,
                bold=True,
            )
        )

        self.TMP: set[Drone] = set()

    def on_update(self, delta_time: float) -> None:
        """Advances animation and simulation state each frame.

        Interpolates drone sprites toward their target zone centres at a
        frame-rate-independent speed.  For restricted-zone transits the
        drone animates to the midpoint on the first turn (``cost2 = 1``)
        and completes the journey from the midpoint on the second turn
        (``f = 1``).  Once all drones in the current turn have reached
        their destinations, the turn counter is incremented.

        On both auto-reset (counter reaches the last turn) and manual
        restart (R key), drone positions are returned to the start hub and
        ``TMP`` is cleared so that arriving drones are drawn correctly on
        replay.

        Also manages looped audio playback and releases the player handle
        whenever sound is stopped to prevent stale references.

        Args:
            delta_time: Seconds elapsed since the previous frame.
        """
        if self.player and not self.play:
            arcade.stop_sound(self.player)
            self.player = None
        if self.counter == len(self.turns):
            self.play = False
            self.counter = 0
            self.turn = self.turns[self.counter]
            self.TMP.clear()
            for drone in self.graph.drones:
                drone.x = self.graph.start_hub.x
                drone.y = self.graph.start_hub.y

        if self.play or self.next:
            arrived = True
            for mv in self.turn:
                assert isinstance(mv['drones'], list)
                for drone in mv['drones']:
                    assert isinstance(mv['from'], Zone)
                    assert isinstance(mv['to'], Zone)
                    x1: float
                    x2: float
                    y1: float
                    y2: float
                    if mv['cost2']:
                        x1 = mv['from'].x
                        if mv['to'].x == x1:
                            x2 = mv['to'].x
                        else:
                            x2 = (mv['to'].x + x1) / 2
                        y1 = mv['from'].y
                        if mv['to'].y == y1:
                            y2 = mv['to'].y
                        else:
                            y2 = (mv['to'].y + y1) / 2
                    elif mv['f']:
                        x2 = mv['to'].x
                        if mv['from'].x == x2:
                            x1 = mv['from'].x
                        else:
                            x1 = (x2 + mv['from'].x) / 2
                        y2 = mv['to'].y
                        if mv['from'].y == y2:
                            y1 = mv['from'].y
                        else:
                            y1 = (y2 + mv['from'].y) / 2
                    else:
                        x1 = mv['from'].x
                        x2 = mv['to'].x
                        y1 = mv['from'].y
                        y2 = mv['to'].y

                    distance = sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
                    dx = x2 - drone.x
                    dy = y2 - drone.y
                    remain = sqrt(dx ** 2 + dy ** 2)

                    if remain < 0.1:
                        drone.x = x2
                        drone.y = y2
                    else:
                        drone.x += (dx / remain) * delta_time * distance
                        drone.y += (dy / remain) * delta_time * distance
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
            self.TMP.clear()
            for drone in self.graph.drones:
                drone.x = self.graph.start_hub.x
                drone.y = self.graph.start_hub.y

        if (
            self.play_sound
            and self.player
            and not arcade.Sound.is_playing(self.sound, self.player)
        ):
            self.player = arcade.play_sound(self.sound)

        if not self.play_sound:
            if self.player:
                arcade.stop_sound(self.player)
                self.player = None

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

    def on_draw(self) -> None:
        """Renders one frame: graph edges, zone nodes, drone sprites, and HUD.

        Drawing order (back to front):

        1. Connection lines (black) using the world camera.
        2. Zone circles with colour-coded outlines.
        3. Zone name labels.
        4. Drone sprite and ID labels at interpolated positions.
        5. HUD text and button sprites using the fixed GUI camera.
        """
        self.clear()
        self.camera.use()

        for conn in self.graph.connections:
            arcade.draw_line(
                conn.from_zone.x * 300,
                conn.from_zone.y * 600,
                conn.to_zone.x * 300,
                conn.to_zone.y * 600,
                arcade.color.BLACK,
                6,
            )

        for hub in self.graph.hubs.values():
            if hub.color == 'none':
                hub.color = 'white'
            radius = 90
            arcade.draw_circle_outline(
                hub.x * 300, hub.y * 600, radius + 30,
                arcade.color.BLUE_SAPPHIRE, 10
            )
            arcade.draw_circle_filled(
                hub.x * 300, hub.y * 600, radius, arcade.color.WHITE_SMOKE
            )
            arcade.draw_circle_outline(
                hub.x * 300,
                hub.y * 600,
                radius,
                webcolors.name_to_rgb(hub.color),
                60,
            )

        for label in self.labels:
            label.draw()

        for drone in self.graph.drones:
            self.drone.center_x = drone.x * 300
            self.drone.center_y = drone.y * 600
            if (drone.x == self.graph.start_hub.x
                    and drone.y == self.graph.start_hub.y):
                if not drone.id == self.graph.nb_drones:
                    continue
            elif (drone.x == self.graph.end_hub.x
                    and drone.y == self.graph.end_hub.y):
                if drone in self.TMP:
                    continue
                else:
                    self.TMP.add(drone)
            arcade.draw_sprite(self.drone)

            for txt in self.dronenb:
                txt.text = str(drone.id)
                i = 0
                for dx, dy in [
                    (0.003, 0),
                    (-0.003, 0),
                    (0, 0.003),
                    (0, -0.003),
                    (0, 0),
                ]:
                    self.dronenb[i].x = (drone.x + 0.026 + dx) * 300
                    self.dronenb[i].y = (drone.y + 0.026 + dy) * 600
                    i += 1

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

    def on_mouse_scroll(
        self, x: float, y: float, scroll_x: float, scroll_y: float
    ) -> None:
        """Zooms the world camera in or out on mouse scroll.

        Each scroll step multiplies or divides the zoom factor by 1.1,
        giving smooth geometric scaling centred on the current view.

        Args:
            x: Mouse X position at the time of the scroll event.
            y: Mouse Y position at the time of the scroll event.
            scroll_x: Horizontal scroll delta (unused).
            scroll_y: Vertical scroll delta — positive zooms in, negative
                zooms out.
        """
        if scroll_y > 0:
            self.camera.zoom *= 1.1
        else:
            self.camera.zoom *= 0.9

    def on_mouse_drag(
        self,
        x: int,
        y: int,
        dx: int,
        dy: int,
        buttons: int,
        modifiers: int,
    ) -> None:
        """Pans the world camera while the left mouse button is held.

        The camera offset is adjusted by the drag delta divided by the
        current zoom level so that panning speed remains constant
        regardless of zoom.

        Args:
            x: Current mouse X position.
            y: Current mouse Y position.
            dx: Pixel change in X since the last drag event.
            dy: Pixel change in Y since the last drag event.
            buttons: Bitmask of currently pressed mouse buttons.
            modifiers: Bitmask of currently held modifier keys.
        """
        if buttons & arcade.MOUSE_BUTTON_LEFT:
            pos = self.camera.position
            self.camera.position = (
                pos.x - (dx / self.camera.zoom),
                pos.y - (dy / self.camera.zoom),
            )

    def on_key_press(self, key: int, modifiers: int) -> None:
        """Handles keyboard shortcuts for simulation playback control.

        Key bindings:

        * **SPACE** — toggle play / pause.  Starts or stops audio in sync
          with the current sound-toggle state.
        * **R** — restart the simulation from turn 0, stopping any audio.
        * **TAB** — toggle background music on or off.
        * **RIGHT arrow** — advance exactly one turn while paused.

        Args:
            key: Arcade key constant for the pressed key.
            modifiers: Bitmask of currently held modifier keys.
        """
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
    """Thin wrapper that constructs the Window and starts the arcade event loop.

    Keeping this class separate from Window allows the simulation pipeline
    (parse → simulate → visualise) to remain decoupled: the engine never
    imports arcade, and tests can skip visualisation entirely.
    """

    @staticmethod
    def run(
        width: int,
        height: int,
        graph: Graph,
        turns: list[list[dict[str, list[Drone] | Zone | int]]],
    ) -> None:
        """Creates the Window and enters the arcade event loop.

        This call blocks until the user closes the window.

        Args:
            width: Desired window width in pixels.
            height: Desired window height in pixels.
            graph: The parsed routing network.
            turns: The movement timeline returned by :meth:`~engine.Engine.simulator`.
        """
        Window(width, height, graph, turns)
        arcade.run()
