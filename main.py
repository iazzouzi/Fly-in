from parsing import Parser

def main() -> None:
    map = Parser.file_parser()
    print(map)

main()