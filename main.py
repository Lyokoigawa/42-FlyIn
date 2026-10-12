from src.parser import FlyInParser
from src.graph import Graph
from src.drone import DroneSystem
import argparse


def main() -> None:
    def_map = "maps/easy/01_linear_path.txt"
    args = argparse.ArgumentParser()
    args.add_argument("--map", type=str, default=def_map,
                      required=False, help="Map to be loaded.")
    args.add_argument("--visual", type=int, default=0,
                      required=False, help="Load pygame visuals")
    map = args.parse_args()
    parsed_map = FlyInParser(map.map)
    parsed_map.read_config()
    fly_in_map = Graph(parsed_map)
    fly_in_map.find_path()
    drones = DroneSystem(parsed_map.configs["nb_drones"], fly_in_map)
    history = drones.simulate(drones)
    if map.visual == 1:
        try:
            from src.visuals import run
            run(fly_in_map, history)
        except ModuleNotFoundError as e:
            print(f"WARNING: {repr(e.name)} module not found.")
            if e.name == "pygame":
                print("Please run 'make install'... I've prepared a whole venv"
                      " for you to play around with pygame in and stuff...")


if __name__ == "__main__":
    main()
