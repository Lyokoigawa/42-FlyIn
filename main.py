from src.parser import FlyInParser
from src.graph import Graph
from src.drone import DroneSystem
import argparse


def main() -> None:
    """Parse the given map, build it, then run an algorithm.

    Runs a quick simulation of a fleet of drones through a given map in
    --map in order to find the cheapest path from start to end in the map.
    It first parses the map and then it gives it to the builder in order
    to build the map then finally passing it to the algorithm, where it will
    calculate the cheapest path and run the drones through it.
    Rerouting if needed.
    Optionally runs visualizer using pygame with --visual in order to help
    understand each move better.
    """

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
