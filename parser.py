from sys import argv
from zone import Zone
from graph import Graph
from connection import Connection
import webcolors  # # type: ignore[import-untyped]


class Parser:
    """Parses input files and builds the drone routing network graph.

    This class handles reading and validating the input file format,
    extracting zone definitions, connections, and metadata, then
    constructing the network graph used by the simulation engine.
    """

    @staticmethod
    def line_parser(
        line: str,
        line_nb: int,
        graph: Graph,
        hub_names: set[str],
        hub_cords: set[tuple[int, int]],
        flags: dict[str, bool],
    ) -> None:
        """Parses a single line from the input file and updates the graph
        structure.

        Processes syntax for metadata configurations including 'nb_drones',
        'start_hub', 'end_hub', 'hub', and 'connection'. Validates all
        syntax according to the subject rules.

        Args:
            line (str): The raw string line extracted from the input text
                file.
            line_nb (int): The current line number, used for verbose error
                reporting.
            graph (Graph): The active graph structure being populated.
            hub_names (set[str]): An accumulated set of previously defined
                hub names to prevent duplicates.
            flags (dict[str, bool]): State dictionary tracking parsing
                progression (e.g., 'start_f').

        Raises:
            SystemExit: If the line contains invalid syntax, duplicate
                definitions, illegal characters (e.g., '-' in names), or
                missing metadata. Prints a descriptive error to stderr.
        """
        if not line:
            return
        KEYS = {'start_hub', 'end_hub', 'hub', 'connection'}
        if line.startswith('#'):
            return
        if '#' in line:
            line = line.split('#', 1)[0]
        if line.count(':') != 1:
            raise SystemExit(
                f"Error: Invalid line format, there must be exactly one "
                f"':' in the line '{line_nb}'"
            )
        key, value = line.split(':')
        key = key.strip()
        value = value.strip()
        if not key:
            raise SystemExit(
                f"Error: Key cannot be empty in line '{line_nb}'"
            )
        if not value:
            raise SystemExit(
                f"Error: Value cannot be empty in line '{line_nb}'"
            )
        if flags['nb_drones_f']:
            if key != 'nb_drones':
                raise SystemExit(
                    f"Error: First line must be nb_drones in line "
                    f"'{line_nb}'"
                )
            try:
                if int(value) <= 0:
                    raise SystemExit(
                        f"Error: nb_drones must be a positive integer in "
                        f"line '{line_nb}'"
                    )
                graph.nb_drones = int(value)
            except ValueError:
                raise SystemExit(
                    f"Error: nb_drones must be an integer in line "
                    f"'{line_nb}'"
                )
            flags['nb_drones_f'] = False
            return
        if key not in KEYS:
            raise SystemExit(
                f"Error: Invalid key '{key}' in line '{line_nb}'"
            )
        if key in {'start_hub', 'end_hub', 'hub'}:
            if key == 'start_hub' and flags['start_f']:
                raise SystemExit(
                    f"Error: start_hub cannot be repeated in line "
                    f"'{line_nb}'"
                )
            if key == 'end_hub' and flags['end_f']:
                raise SystemExit(
                    f"Error: end_hub cannot be repeated in line "
                    f"'{line_nb}'"
                )
            try:
                name, x, y, *metadata = value.split()
            except ValueError:
                raise SystemExit(
                    f"Error: Invalid hub format in line '{line_nb}'"
                )
            if '-' in name:
                raise SystemExit(
                    f"Error: Hub name cannot contain '-' in line "
                    f"'{line_nb}'"
                )
            if name in hub_names:
                raise SystemExit(
                    f"Error: Hub name '{name}' is already used in line "
                    f"'{line_nb}'"
                )
            hub_names.add(name)
            try:
                if (int(x), int(y)) in hub_cords:
                    raise SystemExit(
                        f"Error: Hub coordinates ({x}, {y}) are already "
                        f"used in line '{line_nb}'"
                    )
                hub_cords.add((int(x), int(y)))
                graph.hubs[name] = Zone(name, int(x), int(y))
            except ValueError:
                raise SystemExit(
                    f"Error: Hub coordinates must be integers in line "
                    f"'{line_nb}'"
                )
            if key == 'start_hub':
                graph.hubs[name].is_start = True
                graph.start_hub = graph.hubs[name]
                flags['start_f'] = True
            if key == 'end_hub':
                graph.hubs[name].is_end = True
                graph.end_hub = graph.hubs[name]
                flags['end_f'] = True
            if not metadata:
                return
            metadata_keys = {'color', 'max_drones', 'zone'}
            if not metadata[0].startswith('[') or not metadata[
                -1
            ].endswith(']'):
                raise SystemExit(
                    f"Error: Metadata must be enclosed in [] in line "
                    f"'{line_nb}'"
                )
            metadata[0] = metadata[0].lstrip('[')
            metadata[-1] = metadata[-1].rstrip(']')
            color_f = False
            max_drones_f = False
            zone_f = False
            for item in metadata:
                if item.count('=') != 1:
                    raise SystemExit(
                        f"Error: Invalid metadata format in line "
                        f"'{line_nb}'"
                    )
                ikey, ivalue = item.split('=')
                ikey = ikey.strip()
                ivalue = ivalue.strip()
                if not ikey:
                    raise SystemExit(
                        f"Error: Metadata key cannot be empty in line "
                        f"'{line_nb}'"
                    )
                if not ivalue:
                    raise SystemExit(
                        f"Error: Metadata value cannot be empty in line "
                        f"'{line_nb}'"
                    )
                if ikey not in metadata_keys:
                    raise SystemExit(
                        f"Error: Invalid metadata key '{ikey}' in line "
                        f"'{line_nb}'"
                    )
                if ikey == 'color':
                    if color_f:
                        raise SystemExit(
                            f"Error: color metadata cannot be repeated in "
                            f"line '{line_nb}'"
                        )
                    try:
                        webcolors.name_to_rgb(ivalue)
                    except ValueError:
                        raise SystemExit(
                            f"Error: Invalid color name '{ivalue}' in line "
                            f"'{line_nb}'"
                        )
                    graph.hubs[name].color = ivalue
                    color_f = True
                if ikey == 'max_drones':
                    if max_drones_f:
                        raise SystemExit(
                            f"Error: max_drones metadata cannot be repeated "
                            f"in line '{line_nb}'"
                        )
                    try:
                        if int(ivalue) <= 0:
                            raise SystemExit(
                                f"Error: max_drones must be a positive "
                                f"integer in line '{line_nb}'"
                            )
                        graph.hubs[name].max_drones = int(ivalue)
                        if (
                            key in {'start_hub', 'end_hub'}
                            and int(ivalue) != graph.nb_drones
                        ):
                            raise SystemExit(
                                f"Error: max_drones for start_hub and "
                                f"end_hub must be equal nb_drones in line "
                                f"'{line_nb}'"
                            )
                        max_drones_f = True
                    except ValueError:
                        raise SystemExit(
                            f"Error: max_drones must be an integer in line "
                            f"'{line_nb}'"
                        )
                if ikey == 'zone':
                    if zone_f:
                        raise SystemExit(
                            f"Error: zone metadata cannot be repeated in "
                            f"line '{line_nb}'"
                        )
                    if ivalue not in {
                        'normal',
                        'blocked',
                        'restricted',
                        'priority',
                    }:
                        raise SystemExit(
                            f"Error: Invalid zone value in line "
                            f"'{line_nb}'"
                        )
                    graph.hubs[name].zone = ivalue
                    if ivalue == 'restricted':
                        graph.hubs[name].cost = 2.0
                    elif ivalue == 'priority':
                        graph.hubs[name].cost = 0.2
                    zone_f = True
        if key == 'connection':
            if value.count(' ') > 1:
                raise SystemExit(
                    f"Error: Invalid connection format in line '{line_nb}'"
                )
            if len(value.split()) == 1:
                connection = value
                max_link_capacity = None
            else:
                connection, max_link_capacity = value.split()
            if connection.count('-') != 1:
                raise SystemExit(
                    f"Error: Invalid connection format there must be "
                    f"exactly one '-' in the connection in line "
                    f"'{line_nb}'"
                )
            if not connection.split('-')[0] or not connection.split(
                '-'
            )[1]:
                raise SystemExit(
                    f"Error: Connection must have a from and to hub in "
                    f"line '{line_nb}'"
                )
            if connection.split('-')[0] == connection.split('-')[1]:
                raise SystemExit(
                    f"Error: Connection cannot be between the same hub in "
                    f"line '{line_nb}'"
                )
            from_hub, to_hub = connection.split('-')
            for conn in graph.connections:
                if {
                    conn.from_zone.name,
                    conn.to_zone.name,
                } == {
                    from_hub,
                    to_hub,
                } or {
                    conn.from_zone.name,
                    conn.to_zone.name,
                } == {to_hub, from_hub}:
                    raise SystemExit(
                        f"Error: Connection '{from_hub}-{to_hub}' is "
                        f"duplicated in line '{line_nb}'"
                    )
            if (
                connection.split('-')[0] in hub_names
                and connection.split('-')[1] in hub_names
            ):
                from_shub = graph.hubs[connection.split('-')[0]]
                to_shub = graph.hubs[connection.split('-')[1]]
            else:
                raise SystemExit(
                    "Error: Connection hubs must be defined in the "
                    f"hubs section in line '{line_nb}'"
                )
            if max_link_capacity:
                if max_link_capacity.count('=') != 1:
                    raise SystemExit(
                        f"Error: Invalid max_link_capacity format in "
                        f"line '{line_nb}'"
                    )
                if (
                    not max_link_capacity.startswith('[')
                    or not max_link_capacity.endswith(']')
                ):
                    raise SystemExit(
                        f"Error: max_link_capacity must be enclosed in "
                        f"[] in line '{line_nb}'"
                    )
                max_link_capacity = (
                    max_link_capacity.lstrip('[').rstrip(']')
                )
                if max_link_capacity.split('=')[0] != 'max_link_capacity':
                    raise SystemExit(
                        f"Error: Invalid max_link_capacity format in "
                        f"line '{line_nb}'"
                    )
                try:
                    max_val = int(max_link_capacity.split('=')[1])
                    if max_val <= 0:
                        raise SystemExit(
                            f"Error: max_link_capacity must be a positive "
                            f"integer in line '{line_nb}'"
                        )
                    capacity = max_val
                except ValueError:
                    raise SystemExit(
                        f"Error: max_link_capacity must be an integer in "
                        f"line '{line_nb}'"
                    )
            else:
                capacity = 1
            graph.connections.append(Connection(from_shub, to_shub, capacity))

    @classmethod
    def file_parser(cls) -> Graph:
        """Opens, reads, and parses the complete input file into a valid Graph.

        Reads the file path provided via command line arguments (`sys.argv`),
        processes each line through `line_parser`, and finally validates
        the integrity of the overall graph (ensuring start and end hubs
        exist) while building the adjacency list.

        Returns:
            Graph: A fully constructed, validated, and linked representation
                of the map.

        Raises:
            SystemExit: If no file argument is provided, if the file is not
                a `.txt`, if the file cannot be found/read, or if the
                graph lacks start/end hubs.
        """
        if len(argv) != 2:
            raise SystemExit("Error: No file provided.")
        file = argv[1]
        if not file.endswith('txt'):
            raise SystemExit("Error: File must be a .txt file.")
        try:
            with open(file, 'r') as f:
                graph = Graph()
                lines = [line.strip() for line in f]
                hub_names: set[str] = set()
                hub_cords: set[tuple[int, int]] = set()
                flags = {'start_f': False, 'end_f': False, 'nb_drones_f': True}
                for line_nb, line in enumerate(lines):
                    cls.line_parser(
                        line, line_nb + 1, graph, hub_names, hub_cords, flags
                    )
            if not graph.start_hub:
                raise SystemExit("Error: start_hub is missing.")
            if not graph.end_hub:
                raise SystemExit("Error: end_hub is missing.")
            for hub in graph.hubs.values():
                if hub.name not in graph.adjacency:
                    graph.adjacency[hub.name] = []
                for connection in graph.connections:
                    if hub is connection.from_zone:
                        if (
                            connection.to_zone
                            not in graph.adjacency[hub.name]
                        ):
                            graph.adjacency[hub.name].append(
                                connection.to_zone
                            )
                    elif hub is connection.to_zone:
                        if (
                            connection.from_zone
                            not in graph.adjacency[hub.name]
                        ):
                            graph.adjacency[hub.name].append(
                                connection.from_zone
                            )
            return graph

        except OSError as e:
            raise SystemExit(
                f"Error: Could not read file '{file}' - {e.strerror}"
            )
