from sys import argv
from typing import Any

class Parser:
    @staticmethod
    def line_parser(raw_line: str, map: dict[str, Any], hub_names: set[str], flags: dict[str, bool]) -> None:
        KEYS = {'start_hub', 'end_hub', 'hub', 'connection'}
        line = raw_line
        if line.count(':') != 1:
            raise SystemExit(f"Error: Invalid line format '{raw_line}', there must be exactly one ':' in the line")
        key, value = line.split(':')
        key = key.strip()
        value = value.strip()
        if not key:
            raise SystemExit(f"Error: Key cannot be empty in line '{raw_line}'")
        if not value:
            raise SystemExit(f"Error: Value cannot be empty in line '{raw_line}'")
        if flags['nb_drones_f']:
            if key != 'nb_drones':
                raise SystemExit(f"Error: First line must be nb_drones in line '{raw_line}'")
            try:
                value = int(value)
                if value <= 0:
                    raise SystemExit(f"Error: nb_drones must be a positive integer in line '{raw_line}'")
            except ValueError:
                raise SystemExit(f"Error: nb_drones must be an integer in line '{raw_line}'")
            map['nb_drones'] = value
            flags['nb_drones_f'] = False
            return
        if key not in KEYS:
            raise SystemExit(f"Error: Invalid key '{key}' in line '{raw_line}'")
        if key in {'start_hub', 'end_hub', 'hub'}:
            if key == 'start_hub':
                if flags['start_f']:
                    raise SystemExit(f"Error: start_hub cannot be repeated in line '{raw_line}'")
                elif not 'start_hub' in map:
                    map[key] = {}
            if key == 'end_hub':
                if flags['end_f']:
                    raise SystemExit(f"Error: end_hub cannot be repeated in line '{raw_line}'")
                elif not 'end_hub' in map:
                    map[key] = {}
            if key == 'hub':
                flags['hub_f'] = True
                if not 'hubs' in map:
                    map['hubs'] = []
                map['hubs'].append({})
            try:
                name, x, y, *metadata = value.split()
            except ValueError:
                pass
            if not name:
                raise SystemExit(f"Error: Hub name cannot be empty in line '{raw_line}'")
            if not x or not y:
                raise SystemExit(f"Error: Hub coordinates cannot be empty in line '{raw_line}'")
            if '-' in name:
                raise SystemExit(f"Error: Hub name cannot contain '-' in line '{raw_line}'")
            if name in hub_names:
                raise SystemExit(f"Error: Hub name '{name}' is already used in line '{raw_line}'")
            else:
                if flags['hub_f']:
                    map['hubs'][-1]['name'] = name
                else:
                    map[key]['name'] = name
                hub_names.add(name)
            try:
                if flags['hub_f']:
                    map['hubs'][-1]['cord'] = (int(x), int(y))
                else:
                    map[key]['cord'] = (int(x), int(y))
            except ValueError:
                raise SystemExit(f"Error: Hub coordinates must be integers in line '{raw_line}'")
            if flags['hub_f']:
                map['hubs'][-1]['color'] = 'none'
                map['hubs'][-1]['max_drones'] = 1
                map['hubs'][-1]['zone'] = 'normal'
            else:
                map[key]['color'] = 'none'
                map[key]['max_drones'] = 1
                map[key]['zone'] = 'normal'
            if not metadata:
                if key == 'start_hub':
                    flags['start_f'] = True
                if key == 'end_hub':
                    flags['end_f'] = True
                return
            metadata_keys = {'color', 'max_drones', 'zone'}
            if not metadata[0].startswith('[') or not metadata[-1].endswith(']'):
                raise SystemExit(f"Error: Metadata must be enclosed in [] in line '{raw_line}'")
            metadata[0] = metadata[0].lstrip('[')
            metadata[-1] = metadata[-1].rstrip(']')
            color_f = False
            max_drones_f = False
            zone_f = False
            for item in metadata:
                if item.count('=') != 1:
                    raise SystemExit(f"Error: Invalid metadata format in line '{raw_line}'")
                ikey, ivalue = item.split('=')
                ikey = ikey.strip()
                ivalue = ivalue.strip()
                if not ikey:
                    raise SystemExit(f"Error: Metadata key cannot be empty in line '{raw_line}'")
                if not ivalue:
                    raise SystemExit(f"Error: Metadata value cannot be empty in line '{raw_line}'")
                if not ikey in metadata_keys:
                    raise SystemExit(f"Error: Invalid metadata key '{ikey}' in line '{raw_line}'")
                if ikey == 'color':
                    if color_f:
                        raise SystemExit(f"Error: color metadata cannot be repeated in line '{raw_line}'")
                    else:
                        if flags['hub_f']:
                            map['hubs'][-1][ikey] = ivalue
                        else:
                            map[key][ikey] = ivalue
                        color_f = True
                if ikey == 'max_drones':
                    if max_drones_f:
                        raise SystemExit(f"Error: max_drones metadata cannot be repeated in line '{raw_line}'")
                    try:
                        ivalue = int(ivalue)
                        if ivalue <= 0:
                            raise SystemExit(f"Error: max_drones must be a positive integer in line '{raw_line}'")
                        if key in {'start_hub', 'end_hub'} and ivalue != map['nb_drones']:
                            raise SystemExit(f"Error: max_drones for start_hub and end_hub must be equal nb_drones in line '{raw_line}'")
                        if flags['hub_f']:
                            map['hubs'][-1][ikey] = ivalue
                        else:
                            map[key][ikey] = map['nb_drones']
                        max_drones_f = True
                    except ValueError:
                        raise SystemExit(f"Error: max_drones must be an integer in line '{raw_line}'")
                if ikey == 'zone':
                    if zone_f:
                        raise SystemExit(f"Error: zone metadata cannot be repeated in line '{raw_line}'")
                    if ivalue not in {'normal', 'blocked', 'restricted', 'priority'}:
                        raise SystemExit(f"Error: Invalid zone value in line '{raw_line}'")
                    if flags['hub_f']:
                        map['hubs'][-1][ikey] = ivalue
                    else:
                        map[key][ikey] = ivalue
                    zone_f = True
            if key == 'start_hub':
                flags['start_f'] = True
            if key == 'end_hub':
                flags['end_f'] = True
            if key == 'hub':
                flags['hub_f'] = False
        if key == 'connection':
            if not 'connections' in map:
                map['connections'] = []
            map['connections'].append({})
            if value.count(' ') > 1:
                raise SystemExit(f"Error: Invalid connection format in line '{raw_line}'")
            if len(value.split()) == 1:
                connection = value
                max_link_capacity = None
            else:
                connection, max_link_capacity = value.split()
            if connection.count('-') != 1:
                raise SystemExit(f"Error: Invalid connection format there must be exactly one '-' in the connection in line '{raw_line}'")
            if not connection.split('-')[0] or not connection.split('-')[1]:
                raise SystemExit(f"Error: Connection must have a from and to hub in line '{raw_line}'")
            if connection.split('-')[0] == connection.split('-')[1]:
                raise SystemExit(f"Error: Connection cannot be between the same hub in line '{raw_line}'")
            try:
                from_hub, to_hub = connection.split('-')
            except ValueError:
                raise SystemExit(f"Error: Invalid connection format in line '{raw_line}'")
            for conn in map.get('connections', []):
                if not conn:
                    break
                if {conn["from"], conn["to"]} == {from_hub, to_hub} or {conn["from"], conn["to"]} == {to_hub, from_hub}:
                    raise SystemExit(f"Error: Connection '{from_hub}-{to_hub}' is duplicated in line '{raw_line}'")
            if connection.split('-')[0] in hub_names and connection.split('-')[1] in hub_names:
                map['connections'][-1]['from'] = connection.split('-')[0]
                map['connections'][-1]['to'] = connection.split('-')[1]
            else:
                raise SystemExit(f"Error: Connection hubs must be defined in the hubs section in line '{raw_line}'")
            if max_link_capacity:
                if max_link_capacity.count('=') != 1:
                    raise SystemExit(f"Error: Invalid max_link_capacity format in line '{raw_line}'")
                if not max_link_capacity.startswith('[') or not max_link_capacity.endswith(']'):
                    raise SystemExit(f"Error: max_link_capacity must be enclosed in [] in line '{raw_line}'")
                max_link_capacity = max_link_capacity.lstrip('[').rstrip(']')
                if max_link_capacity.split('=')[0] != 'max_link_capacity':
                    raise SystemExit(f"Error: Invalid max_link_capacity format in line '{raw_line}'")
                try:
                    value = int(max_link_capacity.split('=')[1])
                    if value <= 0:
                        raise SystemExit(f"Error: max_link_capacity must be a positive integer in line '{raw_line}'")
                except ValueError:
                    raise SystemExit(f"Error: max_link_capacity must be an integer in line '{raw_line}'")
                map['connections'][-1]['max_link_capacity'] = value
            else:
                map['connections'][-1]['max_link_capacity'] = 1

    @classmethod
    def file_parser(cls) -> dict[str, Any]:
        if len(argv) != 2:
            raise SystemExit("Error: No file provided.")
        file = argv[1]
        if not file.endswith('txt'):
            raise SystemExit("Error: File must be a .txt file.")
        try:
            with open(file, 'r') as file:
                map = {}
                lines = [line.strip() for line in file if line.strip() and not line.strip().startswith("#")]
                hub_names = set()
                flags = {'start_f': False, 'end_f': False, 'hub_f': False, 'nb_drones_f': True}
                for line in lines:
                    cls.line_parser(line, map, hub_names, flags)
            return map
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