from sys import argv
from zone import Zone
from graph import Graph
from connection import Connection
import webcolors  # # type: ignore[import-untyped]


class Parser:
    """Parses input map files and builds the drone routing network graph.

    Reads and validates the custom text format describing zones, connections,
    and simulation parameters, then constructs the Graph used by the Engine.
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
        """Parses one line from the input file and updates the graph in place.

        Handles the five recognised prefixes: ``nb_drones``, ``start_hub``,
        ``end_hub``, ``hub``, and ``connection``. Blank lines and comments
        (``#``) are silently skipped.  Inline comments are stripped before
        processing.

        Args:
            line: Raw text line read from the input file.
            line_nb: 1-based line number used in error messages.
            graph: Mutable graph being populated during parsing.
            hub_names: Accumulated set of zone names already defined,
                used to detect duplicates.
            hub_cords: Accumulated set of ``(x, y)`` coordinate pairs
                already used, used to detect duplicate positions.
            flags: Parsing-state dictionary with three boolean keys:
                ``'nb_drones_f'`` (True until the first line is consumed),
                ``'start_f'`` (True once a ``start_hub`` has been parsed),
                and ``'end_f'`` (True once an ``end_hub`` has been parsed).

        Raises:
            SystemExit: On any syntax violation, duplicate definition,
                capacity error, or unknown key/value.  The message always
                includes the line number and a description of the cause.
        """
        if not line:
            return
        KEYS = {'start_hub', 'end_hub', 'hub', 'connection'}
        if line.startswith('#'):
            return
        if '#' in line:
            line = line.split('#', 1)[0].strip()
        if line.count(':') != 1:
            raise SystemExit(
                f"Error on line {line_nb}: expected exactly one ':' "
                f"separator, got {line.count(':')}."
            )
        key, value = line.split(':')
        key = key.strip()
        value = value.strip()
        if not key:
            raise SystemExit(
                f"Error on line {line_nb}: key before ':' cannot be empty."
            )
        if not value:
            raise SystemExit(
                f"Error on line {line_nb}: value after ':' cannot be empty."
            )
        if flags['nb_drones_f']:
            if key != 'nb_drones':
                raise SystemExit(
                    f"Error on line {line_nb}: first non-comment line must "
                    f"be 'nb_drones: <positive_integer>', got '{key}'."
                )
            try:
                nb = int(value)
                if nb <= 0:
                    raise SystemExit(
                        f"Error on line {line_nb}: 'nb_drones' must be a "
                        f"positive integer, got {value!r}."
                    )
                graph.nb_drones = nb
            except ValueError:
                raise SystemExit(
                    f"Error on line {line_nb}: 'nb_drones' must be an "
                    f"integer, got {value!r}."
                )
            flags['nb_drones_f'] = False
            return
        if key not in KEYS:
            raise SystemExit(
                f"Error on line {line_nb}: unknown key '{key}'; "
                f"expected one of: start_hub, end_hub, hub, connection."
            )
        if key in {'start_hub', 'end_hub', 'hub'}:
            if key == 'start_hub' and flags['start_f']:
                raise SystemExit(
                    f"Error on line {line_nb}: 'start_hub' is already "
                    f"defined — only one start zone is allowed."
                )
            if key == 'end_hub' and flags['end_f']:
                raise SystemExit(
                    f"Error on line {line_nb}: 'end_hub' is already "
                    f"defined — only one end zone is allowed."
                )
            try:
                name, x, y, *metadata = value.split()
            except ValueError:
                raise SystemExit(
                    f"Error on line {line_nb}: invalid hub format; "
                    f"expected '<name> <x> <y> [metadata]'."
                )
            if '-' in name:
                raise SystemExit(
                    f"Error on line {line_nb}: zone name '{name}' contains "
                    f"'-', which is forbidden (reserved as connection "
                    f"separator)."
                )
            if name in hub_names:
                raise SystemExit(
                    f"Error on line {line_nb}: zone name '{name}' is "
                    f"already defined."
                )
            hub_names.add(name)
            try:
                ix, iy = int(x), int(y)
                if (ix, iy) in hub_cords:
                    raise SystemExit(
                        f"Error on line {line_nb}: coordinates ({x}, {y}) "
                        f"are already occupied by another zone."
                    )
                hub_cords.add((ix, iy))
                graph.hubs[name] = Zone(name, ix, iy)
            except ValueError:
                raise SystemExit(
                    f"Error on line {line_nb}: zone coordinates must be "
                    f"integers, got '{x}' and '{y}'."
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
            tmp = []
            for word in metadata:
                for ch in word:
                    if ch == '[' or ch == ']':
                        tmp.append(ch)
            if tmp[0] != '[' or tmp[1] != ']' or len(tmp) != 2:
                raise SystemExit(
                    f"Error on line {line_nb}: metadata must be enclosed "
                    f"in exactly one pair of brackets '[...]'."
                )
            if not metadata[0].startswith('['):
                raise SystemExit(
                    f"Error on line {line_nb}: metadata block must open "
                    f"with '['."
                )
            if not metadata[-1].endswith(']'):
                raise SystemExit(
                    f"Error on line {line_nb}: metadata block must close "
                    f"with ']'."
                )
            if metadata[0] == '[':
                metadata.pop(0)
            elif metadata[0].startswith('['):
                metadata[0] = metadata[0].lstrip('[')
            if metadata[-1] == ']':
                metadata.pop(-1)
            elif metadata[-1].endswith(']'):
                metadata[-1] = metadata[-1].rstrip(']')
            if not metadata:
                return
            color_f = False
            max_drones_f = False
            zone_f = False
            for item in metadata:
                if item.count('=') != 1:
                    raise SystemExit(
                        f"Error on line {line_nb}: each metadata entry must "
                        f"have exactly one '=', got '{item}'."
                    )
                ikey, ivalue = item.split('=')
                ikey = ikey.strip()
                ivalue = ivalue.strip()
                if not ikey:
                    raise SystemExit(
                        f"Error on line {line_nb}: metadata key cannot be "
                        f"empty in '{item}'."
                    )
                if not ivalue:
                    raise SystemExit(
                        f"Error on line {line_nb}: metadata value cannot be "
                        f"empty in '{item}'."
                    )
                if ikey not in metadata_keys:
                    raise SystemExit(
                        f"Error on line {line_nb}: unknown metadata key "
                        f"'{ikey}'; valid keys are: zone, color, max_drones."
                    )
                if ikey == 'color':
                    if color_f:
                        raise SystemExit(
                            f"Error on line {line_nb}: 'color' metadata key "
                            f"cannot appear more than once."
                        )
                    try:
                        webcolors.name_to_rgb(ivalue)
                    except ValueError:
                        raise SystemExit(
                            f"Error on line {line_nb}: '{ivalue}' is not a "
                            f"recognised CSS color name."
                        )
                    graph.hubs[name].color = ivalue
                    color_f = True
                if ikey == 'max_drones':
                    if max_drones_f:
                        raise SystemExit(
                            f"Error on line {line_nb}: 'max_drones' metadata "
                            f"key cannot appear more than once."
                        )
                    try:
                        md_val = int(ivalue)
                        if md_val <= 0:
                            raise SystemExit(
                                f"Error on line {line_nb}: 'max_drones' must "
                                f"be a positive integer, got {ivalue!r}."
                            )
                    except ValueError:
                        raise SystemExit(
                            f"Error on line {line_nb}: 'max_drones' must be "
                            f"an integer, got {ivalue!r}."
                        )
                    if key in {'start_hub', 'end_hub'}:
                        graph.hubs[name].max_drones = graph.nb_drones
                    else:
                        graph.hubs[name].max_drones = md_val
                    max_drones_f = True
                if ikey == 'zone':
                    if zone_f:
                        raise SystemExit(
                            f"Error on line {line_nb}: 'zone' metadata key "
                            f"cannot appear more than once."
                        )
                    valid_types = {
                        'normal', 'blocked', 'restricted', 'priority'}
                    if ivalue not in valid_types:
                        raise SystemExit(
                            f"Error on line {line_nb}: invalid zone type "
                            f"'{ivalue}'; must be one of: "
                            f"normal, blocked, restricted, priority."
                        )
                    graph.hubs[name].zone = ivalue
                    if ivalue == 'restricted':
                        graph.hubs[name].cost = 2.0
                    elif ivalue == 'priority':
                        graph.hubs[name].cost = 0.2
                    zone_f = True
        if key == 'connection':
            connection, *metadata = value.split()
            if connection.count('-') != 1:
                raise SystemExit(
                    f"Error on line {line_nb}: connection must use exactly "
                    f"one '-' separator, e.g. 'zone1-zone2', "
                    f"got '{connection}'."
                )
            parts = connection.split('-')
            if not parts[0] or not parts[1]:
                raise SystemExit(
                    f"Error on line {line_nb}: both sides of the connection "
                    f"must be non-empty zone names."
                )
            if parts[0] == parts[1]:
                raise SystemExit(
                    f"Error on line {line_nb}: a connection cannot link "
                    f"a zone to itself ('{parts[0]}')."
                )
            from_hub, to_hub = parts[0], parts[1]
            for conn in graph.connections:
                if {conn.from_zone.name, conn.to_zone.name} == {
                    from_hub, to_hub
                }:
                    raise SystemExit(
                        f"Error on line {line_nb}: connection "
                        f"'{from_hub}-{to_hub}' is already defined "
                        f"(duplicate connections are forbidden)."
                    )
            if from_hub in hub_names and to_hub in hub_names:
                from_shub = graph.hubs[from_hub]
                to_shub = graph.hubs[to_hub]
            else:
                unknown = from_hub if from_hub not in hub_names else to_hub
                raise SystemExit(
                    f"Error on line {line_nb}: zone '{unknown}' used in "
                    f"connection is not defined."
                )
            capacity = 1
            if metadata:
                tmp = []
                for word in metadata:
                    for ch in word:
                        if ch == '[' or ch == ']':
                            tmp.append(ch)
                if tmp[0] != '[' or tmp[1] != ']' or len(tmp) != 2:
                    raise SystemExit(
                        f"Error on line {line_nb}: connection metadata must "
                        f"be enclosed in exactly one pair of brackets "
                        f"'[...]'."
                    )
                if not metadata[0].startswith('['):
                    raise SystemExit(
                        f"Error on line {line_nb}: connection metadata block "
                        f"must open with '['."
                    )
                if not metadata[-1].endswith(']'):
                    raise SystemExit(
                        f"Error on line {line_nb}: connection metadata block "
                        f"must close with ']'."
                    )
                if metadata[0] == '[':
                    metadata.pop(0)
                elif metadata[0].startswith('['):
                    metadata[0] = metadata[0].lstrip('[')
                if metadata[-1] == ']':
                    metadata.pop(-1)
                elif metadata[-1].endswith(']'):
                    metadata[-1] = metadata[-1].rstrip(']')
                if metadata:
                    if len(metadata) != 1:
                        raise SystemExit(
                            f"Error on line {line_nb}: connection metadata "
                            f"must contain exactly one entry "
                            f"(max_link_capacity=<n>)."
                        )
                    if metadata[0].count('=') != 1:
                        raise SystemExit(
                            f"Error on line {line_nb}: connection metadata "
                            f"entry must contain exactly one '=', "
                            f"got '{metadata[0]}'."
                        )
                    mkey, mval = metadata[0].split('=')
                    if mkey != 'max_link_capacity':
                        raise SystemExit(
                            f"Error on line {line_nb}: unknown connection "
                            f"metadata key '{mkey}'; expected "
                            f"'max_link_capacity'."
                        )
                    try:
                        max_val = int(mval)
                        if max_val <= 0:
                            raise SystemExit(
                                f"Error on line {line_nb}: "
                                f"'max_link_capacity' must be a positive "
                                f"integer, got {mval!r}."
                            )
                        capacity = max_val
                    except ValueError:
                        raise SystemExit(
                            f"Error on line {line_nb}: "
                            f"'max_link_capacity' must be an integer, "
                            f"got {mval!r}."
                        )
            graph.connections.append(Connection(from_shub, to_shub, capacity))

    @classmethod
    def file_parser(cls) -> Graph:
        """Opens, reads, and parses the complete input file into a Graph.

        Reads the file path from ``sys.argv[1]`` (or prompts when omitted),
        delegates each line to :meth:`line_parser`, validates the final
        graph integrity, and builds the adjacency list.

        Returns:
            A fully constructed, validated Graph ready for the Engine.

        Raises:
            SystemExit: If too many CLI arguments are provided, the file
                extension is not ``.txt``, the file cannot be opened, or
                the parsed graph is missing a ``start_hub`` or ``end_hub``.
        """
        if len(argv) > 2:
            raise SystemExit("Error: too many arguments — expected at most "
                             "one file path.")
        if len(argv) == 1:
            file = input("Enter the file path: ")
        else:
            file = argv[1]
        if not file:
            raise SystemExit("Error: no file path provided.")
        if not file.endswith('txt'):
            raise SystemExit(
                f"Error: '{file}' is not a .txt file."
            )
        try:
            with open(file, 'r') as f:
                graph = Graph()
                lines = [line.strip() for line in f]
                hub_names: set[str] = set()
                hub_cords: set[tuple[int, int]] = set()
                flags = {
                    'start_f': False,
                    'end_f': False,
                    'nb_drones_f': True,
                }
                for line_nb, line in enumerate(lines):
                    cls.line_parser(
                        line, line_nb + 1, graph, hub_names, hub_cords, flags
                    )
            if not graph.start_hub:
                raise SystemExit(
                    "Error: no 'start_hub' found — the map must define "
                    "exactly one starting zone."
                )
            if not graph.end_hub:
                raise SystemExit(
                    "Error: no 'end_hub' found — the map must define "
                    "exactly one destination zone."
                )
            for hub in graph.hubs.values():
                if hub.name not in graph.adjacency:
                    graph.adjacency[hub.name] = []
                for connection in graph.connections:
                    if hub is connection.from_zone:
                        if connection.to_zone not in graph.adjacency[hub.name]:
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
                f"Error: could not read '{file}' — {e.strerror}."
            )
