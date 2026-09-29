from .map import Hub, Connection, Hub_Types
from .parser import FlyInParser
from .error import PathfindingException
from typing import Any, Optional
import heapq
import sys


class Graph:
    def __init__(self, map: FlyInParser) -> None:
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
        for hub in visited:
            if hub.type == Hub_Types.END_HUB:
                return True
        return False

    def find_path(self) -> None:
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
        try:
            for conn in self.connections:
                if hub_a in conn and hub_b in conn:
                    return conn
            raise ValueError("ERROR: There is no connection "
                             f"between {hub_a} and {hub_b}")
        except ValueError as e:
            sys.exit(e)  # type: ignore[arg-type]

    def hub_cost(self, hub: Hub) -> float:
        cost = 1
        if hub.zone == "restricted":
            cost += 1
        if hub.type == Hub_Types.END_HUB:
            return cost
        return cost + (hub.curr_drones * 0.2)

    def path_cost(self, path: list[Hub]) -> float:
        cost: float = 0
        for hub in path:
            cost += self.hub_cost(hub)
        return cost

    def check_connection(self, hub_a: Hub, hub_b: Hub) -> bool:
        for conn in self.connections:
            if hub_a in conn and hub_b in conn:
                return True
        return False
