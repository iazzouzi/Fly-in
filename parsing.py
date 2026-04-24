from sys import argv
from typing import Any

class Parser():
    @staticmethod
    def line_parser(line: str, map: dict[str, Any], f: int) -> None:
        KEYS = {'start_hub', 'end_hub', 'hub', 'connection'}
        if not line or line.startswith('#'):
            return
        if not ':' in line or line.count(':') != 1:
            raise SystemExit("Error: Invalid line format")
        key, value = line.split(':')
        key = key.strip()
        value = value.strip()
        if not key:
            raise SystemExit("Error: Key cannot be empty")
        if not value:
            raise SystemExit("Error: Value cannot be empty")
        if f:
            if not key == 'nb_drones':
                raise SystemExit("Error: First line must be nb_drones")
            try:
                value = int(value)
            except ValueError:
                raise SystemExit("Error: nb_drones must be an integer")
            else:
                if value < 0:
                    raise SystemExit("Error: nb_drones must be a positive integer")
                map['nb_drones'] = value
                f = 0
        if key not in KEYS:
            raise SystemExit(f"Error: Invalid key '{key}'")
        if key == 'nb_drones':
            raise SystemExit("Error: nb_drones must be in the first line and cannot be repeated")
        start_f = 0
        end_f = 0
        hub_names = {}
        if key == 'start_hub' or key == 'end_hub' or key == 'hub':
            if key == 'start_hub' and start_f:
                raise SystemExit("Error: start_hub cannot be repeated")
            if key == 'end_hub' and end_f:
                raise SystemExit("Error: end_hub cannot be repeated")
            values = value.split(' ', 13)
            if len(values) != 4:
                raise SystemExit("Error: Invalid start-hub format")
            name, x, y, metadata = values
            if '-' in name or ' ' in name:
                raise SystemExit("Error: Hub name cannot contain '-' or spaces")
            if key == 'hub':
                if name in hub_names:
                    raise SystemExit(f"Error: Hub name '{name}' is already used")
                else:
                    map[key]['name'] = name
                    hub_names.add(name)
            map[key]['name'] = name
            try:
                map[key]['cord'] = (int(x), int(y))
            except ValueError:
                raise SystemExit("Error: Hub coordinates must be integers")
            metadata_keys = {'color', 'max_drones'}
            if key == 'hub':
                metadata_keys.add('zone')
            if not metadata.startswith('[') or not metadata.endswith(']'):
                raise SystemExit("Error: Metadata must be enclosed in []")
            metadata = metadata.strip('[]')
            if metadata.count(' ') > 2:
                raise SystemExit("Error: Metadata in start-hub must contain between 1 and 3 key-value pairs")
            for item in metadata.split(' ', 2):
                if item.count('=') != 1:
                    raise SystemExit("Error: More than one '=' found in metadata item")
                ikey, ivalue = item.split('=', 1)
                ikey = ikey.strip()
                ivalue = ivalue.strip()
                if not ikey:
                    raise SystemExit("Error: Metadata key cannot be empty")
                if not ivalue:
                    raise SystemExit("Error: Metadata value cannot be empty")
                if not ikey in metadata_keys:
                    raise SystemExit(f"Error: Invalid metadata key '{key}'")
                if ikey == 'color':
                    map[key][ikey] = ivalue
                elif ikey == 'max-drones':
                    try:
                        map[key][ikey] = int(ivalue)
                        if map[key][ikey] < 0:
                            raise SystemExit("Error: max-drones must be a positive integer")
                    except ValueError:
                        raise SystemExit("Error: max-drones must be an integer")
                elif ikey == 'zone':
                    if ikey not in {'normal', 'blocked', 'restricted', 'priority'}:
                        raise SystemExit("Error: Invalid zone value")
                    map[key][ikey] = ivalue
            if key == 'start_hub':
                start_f = 1
            if key == 'end_hub':
                end_f = 1


    if len(argv) != 2:
        raise SystemExit("Error: No file provided.")
    file = argv[1]
    if not file.endswith('txt'):
        raise SystemExit("Error: File must be a .txt file.")
    try:
        with open(file, 'r') as f:
            map = {'start-hub': 
                   {'name': str, 'cord': tuple, 'color': str, 'max-drones': int},
                   'end_hub': 
                   {'name': str, 'cord': tuple, 'color': str, 'max-drones': int},
                   'hub':
                    [{'name': str, 'cord': tuple, 'color': str, 'max-drones': int}]}

            lines = [line.strip() for line in f]
            f = 1
            for line in lines:
                line_parser(line, map, f)
    except FileNotFoundError:
        raise SystemExit(f"Error: File '{file}' not found.")
    except PermissionError:
        raise SystemExit(f"Error: Permission denied for file '{file}'.")
    except IOError:
        raise SystemExit(f"Error: Could not read file '{file}'.")
    except Exception as e:
        raise SystemExit(f"Error: {str(e)}")
