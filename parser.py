from sys import argv
from typing import Any
from models.zone import Zone
from models.graph import Graph
from models.connection import Connection

class Parser:
    @staticmethod
    def line_parser(line: str, line_nb: int, result: dict[str, Any], hub_names: set[str], flags: dict[str, bool]) -> None:
        KEYS = {'start_hub', 'end_hub', 'hub', 'connection'}
        if line.startswith('#'):
            return
        if line.count(':') != 1:
            raise SystemExit(f"Error: Invalid line format, there must be exactly one ':' in the line '{line_nb}'")
        key, value = line.split(':')
        key = key.strip()
        value = value.strip()
        if not key:
            raise SystemExit(f"Error: Key cannot be empty in line '{line_nb}'")
        if not value:
            raise SystemExit(f"Error: Value cannot be empty in line '{line_nb}'")
        if flags['nb_drones_f']:
            if key != 'nb_drones':
                raise SystemExit(f"Error: First line must be nb_drones in line '{line_nb}'")
            try:
                value = int(value)
                if value <= 0:
                    raise SystemExit(f"Error: nb_drones must be a positive integer in line '{line_nb}'")
            except ValueError:
                raise SystemExit(f"Error: nb_drones must be an integer in line '{line_nb}'")
            result['nb_drones'] = value
            flags['nb_drones_f'] = False
            return
        if key not in KEYS:
            raise SystemExit(f"Error: Invalid key '{key}' in line '{line_nb}'")
        if key in {'start_hub', 'end_hub', 'hub'}:
            if key == 'start_hub':
                if flags['start_f']:
                    raise SystemExit(f"Error: start_hub cannot be repeated in line '{line_nb}'")
                elif not 'start_hub' in result:
                    result[key] = {}
            if key == 'end_hub':
                if flags['end_f']:
                    raise SystemExit(f"Error: end_hub cannot be repeated in line '{line_nb}'")
                elif not 'end_hub' in result:
                    result[key] = {}
            if key == 'hub':
                flags['hub_f'] = True
                if not 'hubs' in result:
                    result['hubs'] = []
                result['hubs'].append({})
            try:
                name, x, y, *metadata = value.split()
            except ValueError:
                raise SystemExit(f"Error: Invalid hub format in line '{line_nb}'")
            if '-' in name:
                raise SystemExit(f"Error: Hub name cannot contain '-' in line '{line_nb}'")
            if name in hub_names:
                raise SystemExit(f"Error: Hub name '{name}' is already used in line '{line_nb}'")
            else:
                if flags['hub_f']:
                    result['hubs'][-1]['name'] = name
                else:
                    result[key]['name'] = name
                hub_names.add(name)
            try:
                if flags['hub_f']:
                    result['hubs'][-1]['cord'] = (int(x), int(y))
                else:
                    result[key]['cord'] = (int(x), int(y))
            except ValueError:
                raise SystemExit(f"Error: Hub coordinates must be integers in line '{line_nb}'")
            if flags['hub_f']:
                result['hubs'][-1]['color'] = 'none'
                result['hubs'][-1]['max_drones'] = 1
                result['hubs'][-1]['zone'] = 'normal'
            else:
                result[key]['color'] = 'none'
                result[key]['max_drones'] = 1
                result[key]['zone'] = 'normal'
            if not metadata:
                if key == 'start_hub':
                    flags['start_f'] = True
                if key == 'end_hub':
                    flags['end_f'] = True
                if key == 'hub':
                    flags['hub_f'] = False
                return
            metadata_keys = {'color', 'max_drones', 'zone'}
            if not metadata[0].startswith('[') or not metadata[-1].endswith(']'):
                raise SystemExit(f"Error: Metadata must be enclosed in [] in line '{line_nb}'")
            metadata[0] = metadata[0].lstrip('[')
            metadata[-1] = metadata[-1].rstrip(']')
            color_f = False
            max_drones_f = False
            zone_f = False
            for item in metadata:
                if item.count('=') != 1:
                    raise SystemExit(f"Error: Invalid metadata format in line '{line_nb}'")
                ikey, ivalue = item.split('=')
                ikey = ikey.strip()
                ivalue = ivalue.strip()
                if not ikey:
                    raise SystemExit(f"Error: Metadata key cannot be empty in line '{line_nb}'")
                if not ivalue:
                    raise SystemExit(f"Error: Metadata value cannot be empty in line '{line_nb}'")
                if not ikey in metadata_keys:
                    raise SystemExit(f"Error: Invalid metadata key '{ikey}' in line '{line_nb}'")
                if ikey == 'color':
                    if color_f:
                        raise SystemExit(f"Error: color metadata cannot be repeated in line '{line_nb}'")
                    else:
                        if flags['hub_f']:
                            result['hubs'][-1][ikey] = ivalue
                        else:
                            result[key][ikey] = ivalue
                        color_f = True
                if ikey == 'max_drones':
                    if max_drones_f:
                        raise SystemExit(f"Error: max_drones metadata cannot be repeated in line '{line_nb}'")
                    try:
                        ivalue = int(ivalue)
                        if ivalue <= 0:
                            raise SystemExit(f"Error: max_drones must be a positive integer in line '{line_nb}'")
                        if key in {'start_hub', 'end_hub'} and ivalue != result['nb_drones']:
                            raise SystemExit(f"Error: max_drones for start_hub and end_hub must be equal nb_drones in line '{line_nb}'")
                        if flags['hub_f']:
                            result['hubs'][-1][ikey] = ivalue
                        else:
                            result[key][ikey] = result['nb_drones']
                        max_drones_f = True
                    except ValueError:
                        raise SystemExit(f"Error: max_drones must be an integer in line '{line_nb}'")
                if ikey == 'zone':
                    if zone_f:
                        raise SystemExit(f"Error: zone metadata cannot be repeated in line '{line_nb}'")
                    if ivalue not in {'normal', 'blocked', 'restricted', 'priority'}:
                        raise SystemExit(f"Error: Invalid zone value in line '{line_nb}'")
                    if flags['hub_f']:
                        result['hubs'][-1][ikey] = ivalue
                    else:
                        result[key][ikey] = ivalue
                    zone_f = True
            if key == 'start_hub':
                flags['start_f'] = True
            if key == 'end_hub':
                flags['end_f'] = True
            if key == 'hub':
                flags['hub_f'] = False
        if key == 'connection':
            if not 'connections' in result:
                result['connections'] = []
            result['connections'].append({})
            if value.count(' ') > 1:
                raise SystemExit(f"Error: Invalid connection format in line '{line_nb}'")
            if len(value.split()) == 1:
                connection = value
                max_link_capacity = None
            else:
                connection, max_link_capacity = value.split()
            if connection.count('-') != 1:
                raise SystemExit(f"Error: Invalid connection format there must be exactly one '-' in the connection in line '{line_nb}'")
            if not connection.split('-')[0] or not connection.split('-')[1]:
                raise SystemExit(f"Error: Connection must have a from and to hub in line '{line_nb}'")
            if connection.split('-')[0] == connection.split('-')[1]:
                raise SystemExit(f"Error: Connection cannot be between the same hub in line '{line_nb}'")
            from_hub, to_hub = connection.split('-')
            for conn in result.get('connections', [])[:-1]:
                if {conn["from"], conn["to"]} == {from_hub, to_hub} or {conn["from"], conn["to"]} == {to_hub, from_hub}:
                    raise SystemExit(f"Error: Connection '{from_hub}-{to_hub}' is duplicated in line '{line_nb}'")
            if connection.split('-')[0] in hub_names and connection.split('-')[1] in hub_names:
                result['connections'][-1]['from'] = connection.split('-')[0]
                result['connections'][-1]['to'] = connection.split('-')[1]
            else:
                raise SystemExit(f"Error: Connection hubs must be defined in the hubs section in line '{line_nb}'")
            if max_link_capacity:
                if max_link_capacity.count('=') != 1:
                    raise SystemExit(f"Error: Invalid max_link_capacity format in line '{line_nb}'")
                if not max_link_capacity.startswith('[') or not max_link_capacity.endswith(']'):
                    raise SystemExit(f"Error: max_link_capacity must be enclosed in [] in line '{line_nb}'")
                max_link_capacity = max_link_capacity.lstrip('[').rstrip(']')
                if max_link_capacity.split('=')[0] != 'max_link_capacity':
                    raise SystemExit(f"Error: Invalid max_link_capacity format in line '{line_nb}'")
                try:
                    value = int(max_link_capacity.split('=')[1])
                    if value <= 0:
                        raise SystemExit(f"Error: max_link_capacity must be a positive integer in line '{line_nb}'")
                except ValueError:
                    raise SystemExit(f"Error: max_link_capacity must be an integer in line '{line_nb}'")
                result['connections'][-1]['max_link_capacity'] = value
            else:
                result['connections'][-1]['max_link_capacity'] = 1

    @staticmethod
    def graph_gen(result: dict[str, Any]) -> Graph:
        graph = Graph()
        graph.nb_drones = result['nb_drones']

        start_hub = result['start_hub']
        graph.start_hub = Zone(start_hub['name'], start_hub['cord'][0], start_hub['cord'][1], start_hub['zone'], start_hub['max_drones'], start_hub['color'])
        
        end_hub = result['end_hub']
        graph.end_hub = Zone(end_hub['name'], end_hub['cord'][0], end_hub['cord'][1], end_hub['zone'], end_hub['max_drones'], end_hub['color'])
        
        for hub in result.get('hubs', []):
            graph.hubs[hub['name']] = Zone(hub['name'], hub['cord'][0], hub['cord'][1], hub['zone'], hub['max_drones'], hub['color'])
        
        for connection in result.get('connections', []):
            graph.connections.append(Connection(connection['from'], connection['to'], connection['max_link_capacity']))
        
        for hub in graph.hubs.values():
            if not hub.name in graph.adjacency:
                graph.adjacency[hub.name] = []
            for connection in graph.connections:
                if hub.name == connection.from_zone:
                    if not connection.to_zone in graph.adjacency[hub.name]:
                        graph.adjacency[hub.name].append(connection.to_zone)
                elif hub.name == connection.to_zone:
                    if not connection.from_zone in graph.adjacency[hub.name]:
                        graph.adjacency[hub.name].append(connection.from_zone)
        return graph


    @classmethod
    def file_parser(cls) -> Graph:
        if len(argv) != 2:
            raise SystemExit("Error: No file provided.")
        file = argv[1]
        if not file.endswith('txt'):
            raise SystemExit("Error: File must be a .txt file.")
        try:
            with open(file, 'r') as file:
                result = {}
                lines = [line.strip() for line in file if line.strip()]
                hub_names = set()
                flags = {'start_f': False, 'end_f': False, 'hub_f': False, 'nb_drones_f': True}
                for line_nb, line in enumerate(lines):
                    cls.line_parser(line, line_nb+1, result, hub_names, flags)
            if not 'nb_drones' in result:
                raise SystemExit("Error: nb_drones is missing.")
            if not 'start_hub' in result:
                raise SystemExit("Error: start_hub is missing.")
            if not 'end_hub' in result:
                raise SystemExit("Error: end_hub is missing.")
            if not 'hubs' in result:
                result['hubs'] = []
            result['hubs'].insert(0, result['start_hub'])
            result['hubs'].append(result['end_hub'])
            return cls.graph_gen(result)
        except FileNotFoundError:
            raise SystemExit(f"Error: File '{file}' not found.")
        except PermissionError:
            raise SystemExit(f"Error: Permission denied for file '{file}'.")
        except IsADirectoryError:
            raise SystemExit(f"Error: '{file}' is a directory, not a file.")
        except IOError:
            raise SystemExit(f"Error: Could not read file '{file}'.")
        except Exception as e:
            raise SystemExit(f"Error: {str(e)}")