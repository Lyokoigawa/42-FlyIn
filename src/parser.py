from typing import Any, Union
import sys
import re


metadata = re.compile(r"\[([^]]*)]")
hub_name = re.compile(r"^[A-Za-z0-9_]+$")
parse_int = re.compile(r".*[^0-9-]")


class FlyInParser:
    """Parses map configuration text files into structured graph data.

    Reads plain-text map files to extract configuration parameters, hub
    coordinates, metadata settings, and connection paths used for drone
    navigation and simulation.

    Attributes:
        map (str): Filepath of the target map text file to parse.
        configs (dict[str, Any]): Parsed key-value metadata configuration.
        nodes (dict[str, tuple[tuple[int, int], str]]): Parsed hub nodes mapped
            to coordinate tuples and node type identifiers.
        connections (list[list[str]]): List of valid hub connection pairs.
    """

    def __init__(self, map_name: str) -> None:
        """Initializes the FlyInParser instance with a target map filepath.

        Args:
            map_name (str): Filepath of the map file to parse.
        """
        self.map = map_name
        self.configs: dict[str, Any] = {}
        self.nodes: dict[str, tuple[tuple[int, int], str]] = {}
        self.connections: list[list[str]] = []

    def parse_hub(self, hub_data: list[str], line_id: int) -> None:
        """Parses 'hub:' entries in the map file.

        Args:
            hub_data (list[str]): List of parsed string tokens for a hub.
            line_id (int): File line index used for reporting errors.

        Raises:
            ValueError: If hub name is invalid/empty, duplicate start or end
                hubs are found, or coordinates are non-integer values.
        """
        hub_data[0] = hub_data[0].strip(":")
        try:
            if hub_data[0] == "start_hub" or hub_data[0] == "end_hub":
                for v in self.nodes.values():
                    if hub_data[0] == v[1]:
                        raise ValueError(f"Duplicate {hub_data[0]}")
            if len(hub_data[1]) == 0:
                raise ValueError("Hub name cannot be empty")
            if not hub_name.search(hub_data[1]):
                raise ValueError(f"{hub_data[1]} is not a valid hub name")
            if parse_int.search(hub_data[2]) or parse_int.search(hub_data[3]):
                raise ValueError(f"ERROR in line {line_id}: "
                                 f"({hub_data[2]}, {hub_data[3]}) are invalid "
                                 "coordiantes")
            n_node = {hub_data[1]: [[int(hub_data[2]),
                                    int(hub_data[3])],
                                    hub_data[0]]}
            for k, v in self.nodes.items():
                node_value = n_node.get(hub_data[1])
                if (node_value is not None and
                        v[0] == node_value[0][0] and
                        v[1] == node_value[0][1]):
                    curr_item = dict({k: v})
                    raise ValueError(f"ERROR in line {line_id}: "
                                     f"{n_node} must be in a "
                                     f"different position than {curr_item}")
            self.nodes.update(n_node)  # type: ignore[arg-type]
        except ValueError as e:
            sys.exit(f"ERROR in line {line_id + 1}: {e}.")

    def parse_connection(self, con_data: list[str], line_id: int) -> None:
        """Parses 'connection:' entries in the map file.

        Args:
            con_data (list[str]): Parsed tokens for connection data.
            line_id (int): File line index used for reporting errors.

        Raises:
            ValueError: If a node connects to itself, connects unknown hubs,
                or repeats an existing connection path.
        """
        try:
            if con_data[1] == con_data[2]:
                raise ValueError(f"{con_data[1]} cannot connect to itself")
            if con_data[1] not in self.nodes.keys():
                raise ValueError(f"{con_data[1]} is not a real hub name")
            if con_data[2] not in self.nodes.keys():
                raise ValueError(f"{con_data[2]} is not a real hub name")
            curr_con = list([con_data[1], con_data[2]])
            for v in self.connections:
                if curr_con == v[::-1]:
                    raise ValueError("Roundabout connections not allowed.")
                elif curr_con == v:
                    raise ValueError("Connection already exists.")
            self.connections.append(curr_con)
        except ValueError as e:
            sys.exit(f"ERROR in line {line_id + 1}: {e}.")

    def parse_hub_metadata(self, meta_data: list[str], line_id: int) -> None:
        """Parses bracketed hub metadata ('zone', 'max_drones', 'color').

        Args:
            meta_data (list[str]): Parsed tokens containing bracketed metadata.
            line_id (int): File line index used for reporting errors.

        Raises:
            ValueError: If metadata key is unrecognized, value types fail
                validation, or duplicate metadata keys are declared.
        """
        valid_meta = ["zone", "color", "max_drones"]
        valid_zone = ["normal", "blocked", "restricted", "priority"]
        valid_color = ["red", "yellow", "blue", "orange", "green", "purple",
                       "white", "gray", "black", "cyan", "brown", "lime",
                       "magenta", "gold", "maroon", "darkred", "crimson",
                       "violet", "pink", "rainbow", "lightblue"]
        cur_data: dict[str, Union[str | int]] = {}
        try:
            if meta_data[-1].startswith("[") and meta_data[-1].endswith("]"):
                data = meta_data[-1].strip("[]").split(" ")
                for items in data:
                    item: list[Any] = items.split("=")
                    if item[0] not in valid_meta:
                        raise ValueError(f"{item[0]} not valid metadata.")
                    if item[0] in cur_data.keys():
                        raise ValueError("Duplicate metadata keys")
                    if item[0] == "max_drones":
                        if parse_int.search(item[1]):
                            raise ValueError(f"{item[1]} is not a "
                                             "valid number")
                        item[1] = int(item[1])
                        if item[1] < 1:
                            raise ValueError(f"{item[1]} cannot be less "
                                             "than 1")
                        if "start" in meta_data[0] or "end" in meta_data[0]:
                            if item[1] < self.configs.get("nb_drones"):
                                raise ValueError(f"{item[1]} less than "
                                                 "max number of drones")
                    if item[0] == "zone":
                        if item[1] not in valid_zone:
                            raise ValueError(f"{item[0]} is not a "
                                             "valid zone")
                    if item[0] == "color":
                        if item[1] not in valid_color:
                            raise ValueError(f"{item[0]} is not a "
                                             "creative color")
                    cur_data.update({item[0]: item[1]})
                self.configs.update({meta_data[1]: cur_data})
        except ValueError as e:
            sys.exit(f"ERROR in line {line_id + 1}: {e}.")

    def parse_conn_metadata(self, meta_data: list[str], line_id: int) -> None:
        """Parses bracketed connection metadata ('max_link_capacity').

        Args:
            meta_data (list[str]): Parsed tokens containing connection
                metadata.
            line_id (int): File line index used for reporting errors.

        Raises:
            ValueError: If attribute name is invalid or capacity limit is not a
                positive integer.
        """
        valid_meta = "max_link_capacity"
        cur_data: dict[str, Union[str | int]] = {}
        try:
            if meta_data[-1].startswith("[") and meta_data[-1].endswith("]"):
                data = meta_data[-1].strip("[]").split(" ")
                for items in data:
                    item: list[Any] = items.split("=")
                    if item[0] != valid_meta:
                        raise ValueError(f"{item[0]} not valid metadata.")
                    if parse_int.search(item[1]):
                        raise ValueError(f"{item[1]} not a valid number")
                    item[1] = int(item[1])
                    if item[1] < 1:
                        raise ValueError(f"{item[1]} cannot be less than 1")
                    cur_data.update({item[0]: item[1]})
                con_k = str(meta_data[1] + " " + meta_data[2])
                self.configs.update({con_k: cur_data})
        except ValueError as e:
            sys.exit(f"ERROR in line {line_id + 1}: {e}.")

    def read_config(self) -> None:
        """Reads and parses the map configuration file line by line.

        Populates internal state variables ('self.configs', 'self.nodes', and
        'self.connections') with data extracted from the text file.

        Raises:
            FileNotFoundError: If the target map file path does not exist.
            IsADirectoryError: If the target map file path is a directory.
            ValueError: If drone numbers are duplicated or non-positive, if
                lines contain unknown directive prefixes, or if required hubs
                are missing.
        """
        try:
            with open(self.map, "r", encoding="utf-8") as f:
                lines = f.readlines()
        except FileNotFoundError:
            sys.exit(f"ERROR: {self.map} not found.")
        except IsADirectoryError:
            sys.exit(f"ERROR: {self.map} is a directory.")

        try:
            for line_id, line in enumerate(lines):
                if line.startswith("nb_drones:"):
                    if "nb_drones" in self.configs.keys():
                        raise ValueError("Duplicate line. Only 1 'nb_drone' "
                                         "allowed")
                    line = line.strip("\n")
                    nb_drones = line.split(" ")
                    if parse_int.search(nb_drones[1]):
                        raise ValueError(f"{nb_drones[1]} is not a "
                                         "valid number.")
                    if int(nb_drones[1]) < 1:
                        raise ValueError(f"{nb_drones[1]} is not a "
                                         "positive integer.")
                    self.configs.update({"nb_drones": int(nb_drones[1])})
                elif line.startswith("hub:"):
                    line = line.strip("\n")
                    hub_data = line.split(" ", 4)
                    self.parse_hub(hub_data, line_id)
                    self.parse_hub_metadata(hub_data, line_id)
                elif line.startswith("start_hub:"):
                    line = line.strip("\n")
                    hub_data = line.split(" ", 4)
                    self.parse_hub(hub_data, line_id)
                    self.parse_hub_metadata(hub_data, line_id)
                elif line.startswith("end_hub:"):
                    line = line.strip("\n")
                    hub_data = line.split(" ", 4)
                    self.parse_hub(hub_data, line_id)
                    self.parse_hub_metadata(hub_data, line_id)
                elif line.startswith("connection:"):
                    line = line.strip("\n")
                    con_data = line.replace("-", " ").split(" ")
                    self.parse_connection(con_data, line_id)
                    self.parse_conn_metadata(con_data, line_id)
                elif line.startswith("#") or line == "\n":
                    continue
                else:
                    raise ValueError(f"{line[0:line.index(':')]} "
                                     "is not a valid data type")
            last_check: list[str] = []
            for v in self.nodes.values():
                last_check.append(v[1])
            if "start_hub" not in last_check:
                raise ValueError("Missing start_hub")
            if "end_hub" not in last_check:
                raise ValueError("Missing end_hub")
        except ValueError as e:
            sys.exit(f"ERROR in line {line_id + 1}: {e}.")
