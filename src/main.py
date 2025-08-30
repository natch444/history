import sys
from json_to_git import *

def main():
    if len(sys.argv) != 2:
        print("Missing path to config file")
        print("Usage: main.py [file.yml]")
    else:
        read_json(sys.argv[1])


if __name__ == "__main__":
    main()
