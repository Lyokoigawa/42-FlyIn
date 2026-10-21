from .map import Hub, Connection, Hub_Types
from .parser import FlyInParser
from .error import PathfindingException
from typing import Any, Optional
import heapq
import sys


class Graph:
    """Manages graph topology, hubs, connections, and pathfinding algorithms.

    Constructs the navigation graph from parsed map data and handles
    shortest path computation (Dijkstra/A* with priority queues), dynamic
    rerouting, path cost evaluation, and connection state management.

    Attributes:
        hubs (dict[str, Hub]): Map of hub to their corresponding Hub instances.
        connections (list[Connection]): List of connection edges between hubs.
        max_drones (int): Maximum drone capacity allowed by configuration.
        distances (dict[Hub, int]): Calculated shortest paths to visited hubs.
        came_from (dict[Hub, Hub]): Parent map for reconstructing paths.
        start (Hub): Designated starting hub instance.
        end (Hub): Designated ending target hub instance.
    """

    def __init__(self, map: FlyInParser) -> None:
        """Initializes Graph instance using parsed map configuration data.

        Args:
            map (FlyInParser): Parsed map data containing nodes, connections,
                and configuration attributes.
        """
        self.hubs: dict[str, Hub] = {}
        self.connections: list[Connection] = []
        self.max_drones = map.configs["nb_drones"]
        for node, data in map.nodes.items():
            if data[1] == "hub":
                n_hub = Hub(data[1], node, data[0][0],
                            data[0][1], map.configs["nb_drones"])
            else:
                n_hub = Hub(data[1], node, data[0][0],
                            data[0][1], map.configs["nb_drones"])
            if node in map.configs.keys():
                n_hub.set_meta(map.configs[node])
            self.hubs.update({n_hub.name: n_hub})
        for conn in map.connections:
            n_con = Connection(self.hubs[conn[0]], self.hubs[conn[1]])
            meta_key = str(conn[0] + " " + conn[1])
            if meta_key in map.configs.keys():
                config_value = map.configs.get(meta_key)
                if config_value is not None:
                    v = config_value.get("max_link_capacity")
                    n_con.set_meta(v)
            self.connections.append(n_con)

    def is_solvable(self, visited: list[Hub]) -> bool:
        """Checks if the target end hub was reached during pathfinding.

        Args:
            visited (list[Hub]): List of visited hubs during exploration.

        Returns:
            bool: True if destination end hub is within visited list,
            False otherwise.
        """
        for hub in visited:
            if hub.type == Hub_Types.END_HUB:
                return True
        return False

    def find_path(self) -> None:
        """Computes the initial shortest path from start hub to end hub.

        Uses a priority queue to explore graph paths, factoring in zone
        restrictions and priorities. Sets `self.start`, `self.end`,
        `self.distances`, and `self.came_from`.

        Raises:
            SystemExit: If no path can be found to the designated end hub.
        """
        self.distances: dict[Hub, int] = {}
        self.came_from: dict[Hub, Hub] = {}
        exploring: list[Any] = []
        visited: list[Hub] = []
        counter = 0
        for v in self.hubs.values():
            if v.type == Hub_Types.START_HUB:
                self.distances.update({v: 0})
                heapq.heappush(exploring, (0, 1, counter, v))
                counter += 1
        while exploring:
            checking: list[Hub] = []
            cost, is_prio, curr_counter, curr_hub = heapq.heappop(exploring)
            self.distances.update({curr_hub: cost})
            if curr_hub.type == Hub_Types.END_HUB:
                self.end = curr_hub
                visited.append(curr_hub)
                break
            if curr_hub.type == Hub_Types.START_HUB:
                self.start = curr_hub
            for conn in self.connections:
                checking = [con for con in conn.hubs if
                            curr_hub in conn.hubs and
                            con != curr_hub and
                            curr_hub not in visited]
                for candidate in checking:
                    if candidate in visited:
                        continue
                    n_cost = cost
                    n_prio = 1
                    if candidate.zone == "blocked":
                        continue
                    if candidate.zone == "priority":
                        n_prio = 0
                    if candidate.zone == "restricted":
                        n_cost += 2
                    else:
                        n_cost += 1
                    if (candidate not in self.distances or
                            n_cost < self.distances[candidate]):
                        self.distances.update({candidate: n_cost})
                        self.came_from.update({candidate: curr_hub})
                    heapq.heappush(exploring,
                                   (n_cost, n_prio, counter, candidate))
                    counter += 1
            visited.append(curr_hub)
        try:
            if self.is_solvable(visited) is False:
                raise PathfindingException("end_hub inaccessible.")
        except PathfindingException as e:
            sys.exit(f"ERROR: {e} end_Hub unreachable. Clear the map, please.")

    def reroute(self, start: Hub) -> list[Hub]:
        """Calculates an alternate path to the end hub dynamically from a hub.

        Re-evaluates path costs starting from the current hub, considering live
        drone occupancy and zone penalties.

        Args:
            start (Hub): Current hub from which to calculate a reroute.

        Returns:
            list[Hub]: Sequence of hubs forming the new path to destination.
        """
        distances: dict[Hub, float] = {}
        came_from: dict[Hub, Hub] = {}
        exploring: list[Any] = []
        visited: list[Hub] = []
        counter = 0
        for v in self.hubs.values():
            if v == start:
                distances.update({v: 0})
                heapq.heappush(exploring, (0, 1, counter, v))
                counter += 1
        while exploring:
            checking: list[Hub] = []
            cost, is_prio, curr_counter, curr_hub = heapq.heappop(exploring)
            distances.update({curr_hub: cost})
            if curr_hub.type == Hub_Types.END_HUB:
                visited.append(curr_hub)
                break
            if curr_hub.type == Hub_Types.START_HUB:
                self.start = curr_hub
            for conn in self.connections:
                checking = [con for con in conn.hubs if
                            curr_hub in conn.hubs and
                            con != curr_hub and
                            curr_hub not in visited]
                for candidate in checking:
                    if candidate in visited:
                        continue
                    n_cost = cost
                    n_prio = 1
                    if candidate.zone == "blocked":
                        continue
                    if candidate.zone == "priority":
                        n_prio = 0
                    n_cost += self.hub_cost(candidate)
                    if (candidate not in distances or
                            n_cost < distances[candidate]):
                        distances.update({candidate: n_cost})
                        came_from.update({candidate: curr_hub})
                    heapq.heappush(exploring,
                                   (n_cost, n_prio, counter, candidate))
                    counter += 1
            visited.append(curr_hub)
        return self.retrace_steps(self.end, came_from)

    def retrace_steps(self, end_hub: Hub,
                      path: Optional[dict[Hub, Hub]] = None) -> list[Hub]:
        """Reconstructs ordered path list from end hub back to start hub.

        Args:
            end_hub (Hub): The destination target hub.
            path (Optional[dict[Hub, Hub]], optional): Specific parent mapping
                dictionary to use. Defaults to `self.came_from`.

        Returns:
            list[Hub]: Chronological list of Hub objects from origin to target.
        """
        if path:
            came_from = path
        else:
            came_from = self.came_from
        hub = end_hub
        steps: list[Hub] = [end_hub]
        while hub in came_from.keys():
            hub = came_from[hub]
            steps.append(hub)
        steps = steps[::-1]
        return steps

    def get_connection(self, hub_a: Hub, hub_b: Hub) -> Connection:
        """Retrieves Connection instance linking two specific hubs.

        Args:
            hub_a (Hub): First endpoint hub.
            hub_b (Hub): Second endpoint hub.

        Returns:
            Connection: Connection edge connecting hub_a and hub_b.

        Raises:
            SystemExit: If no direct connection exists between the hubs.
        """
        try:
            for conn in self.connections:
                if hub_a in conn and hub_b in conn:
                    return conn
            raise ValueError("ERROR: There is no connection "
                             f"between {hub_a} and {hub_b}")
        except ValueError as e:
            sys.exit(e)  # type: ignore[arg-type]

    def hub_cost(self, hub: Hub) -> float:
        """Calculates dynamic travel traversal cost for visiting a hub.

        Incalculates zone type multipliers and current drone congestion level.

        Args:
            hub (Hub): Target hub to calculate cost for.

        Returns:
            float: Total numeric travel cost value.
        """
        cost = 1
        if hub.zone == "restricted":
            cost += 1
        if hub.type == Hub_Types.END_HUB:
            return cost
        return cost + (hub.curr_drones * 0.2)

    def path_cost(self, path: list[Hub]) -> float:
        """Calculates cumulative cost for traversing a sequence of hubs.

        Args:
            path (list[Hub]): Ordered list of hubs representing a path.

        Returns:
            float: Sum total cost of traversing all hubs in the path.
        """
        cost: float = 0
        for hub in path:
            cost += self.hub_cost(hub)
        return cost

    def check_connection(self, hub_a: Hub, hub_b: Hub) -> bool:
        """Checks if a direct connection edge exists between two hubs.

        Args:
            hub_a (Hub): First endpoint hub.
            hub_b (Hub): Second endpoint hub.

        Returns:
            bool: True if connection exists, False otherwise.
        """
        for conn in self.connections:
            if hub_a in conn and hub_b in conn:
                return True
        return False

    def reset_connections(self) -> None:
        """Resets active link traffic counters across all connections to 0."""
        for conn in self.connections:
            conn.curr_link = 0
