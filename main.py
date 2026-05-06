from parsing import Parser

def main() -> None:
    map = Parser.file_parser()
    print(map['nb_drones'], '\n')
    print(map['start_hub'], '\n')
    for i in range(len(map['hubs'])):
        print(map['hubs'][i])
    print('\n', map['end_hub'], '\n')
    for i in range(len(map['connections'])):
        print(map['connections'][i])

main()