from enum import Enum
from .map import Hub, Connection
from .graph import Graph


class Drone_States(Enum):
    """Represents the operational states of a drone in the system."""

    AT_HUB = "at_hub"
    EN_ROUTE = "en_route"
    ASLEEP = "asleep"


class Blocked(Enum):
    """Indicates reasons why a drone's movement step failed."""

    HUB_FULL = "hub_full"
    CONN_FULL = "conn_full"
    IS_ASLEEP = "is_asleep"


class DroneSystem:
    """Manages and simulates a multi-drone routing and navigation system.

    Initializes a fleet of drones, computes initial paths across a graph
    network, and handles step-by-step turn simulations, including dynamic
    rerouting when connections are blocked.

    Attributes:
        nb_drones (int): The number of drones in the system.
        turns (int): Counter tracking total simulation turns executed.
        map (Graph): The graph representing hubs and connections.
        drones (list[Drone]): List of active drone instances in fleet.
    """

    def __init__(self, nb_drones: int, map: Graph) -> None:
        """Initializes system and calculates initial paths for drones.

        Args:
            nb_drones (int): Total number of drones to initialize.
            map (Graph): Graph containing start hub, end destination,
                and network connections.
        """
        self.nb_drones = nb_drones
        self.turns = 0
        self.map = map
        self.drones: list[Drone] = []
        for n in range(self.nb_drones):
            n_drone = Drone(n + 1, self.map.start, self.map.end)
            n_drone.path_find(self.map)
            self.drones.append(n_drone)

    @staticmethod
    def simulate(dro: "DroneSystem") -> list[dict[str, str]]:
        """Simulates turn-by-turn drone movement to destinations.

        Each turn, drones attempt to move to their next path node. If
        blocked, dynamic rerouting is evaluated, adopting new paths
        only if cost is lower than remaining original path cost.

        Args:
            dro (DroneSystem): System instance to simulate.

        Returns:
            list[dict[str, str]]: Chronological history of frames mapping
            drone IDs to hub names or connection strings.
        """
        i = 0
        frame: dict[str, str] = {}
        for drone in dro.drones:
            frame.update({drone.id: drone.curr_hub.name})
        history: list[dict[str, str]] = [frame.copy()]
        while any(drone.curr_hub != drone.destination
                  for drone in dro.drones):
            i += 1
            turn = ""
            for drone in dro.drones:
                step = None
                path = None
                if drone.curr_hub != drone.destination:
                    next = drone.path.index(drone.curr_hub) + 1
                    path = dro.map.get_connection(drone.curr_hub,
                                                  drone.path[next])
                    step = drone.go_to(drone.path[next], path)
                    if isinstance(step, Blocked):
                        n_path = dro.map.reroute(drone.curr_hub)
                        curr_index = drone.path.index(drone.curr_hub)
                        og_cost = dro.map.path_cost(drone.path[curr_index:])
                        n_cost = dro.map.path_cost(n_path)
                        if n_cost < og_cost:
                            drone.path = n_path
                            next = drone.path.index(drone.curr_hub) + 1
                            path = dro.map.get_connection(drone.curr_hub,
                                                          drone.path[next])
                            step = drone.go_to(drone.path[next], path)
                            if isinstance(step, Blocked):
                                step = ""
                        else:
                            step = ""
                    if step != "":
                        turn += f"{step} "
                if drone.state != Drone_States.EN_ROUTE:
                    frame.update({drone.id: drone.curr_hub.name})
                else:
                    frame.update({drone.id: str(path)})
            history.append(frame.copy())
            dro.turns += 1
            if turn:
                print(turn.strip(" "))
            dro.map.reset_connections()
        print()
        print(f"Total turns: {dro.turns}")
        return history


class Drone:
    """Represents an autonomous drone navigating between hubs in a graph map.

    Tracks the drone's spatial location, operational state, path, and ID,
    while providing methods to transition states and move along connections.

    Attributes:
        id (str): Unique identifier formatted as "D{id}".
        state (Drone_States): Current operational state of the drone.
        curr_hub (Hub): The hub the drone is currently located at or left.
        x (float | int): Current x-coordinate location.
        y (float | int): Current y-coordinate location.
        destination (Hub): The target destination hub.
        idle (int): Counter for turns spent idling.
        path (list[Hub]): Planned path of hubs to reach the destination.
    """

    def __init__(self, id: int, start_hub: Hub, end_hub: Hub) -> None:
        """Initializes a Drone with start/destination hubs and initial state.

        Args:
            id (int): Numerical ID converted to formatted string (e.g., "D1").
            start_hub (Hub): The initial starting hub.
            end_hub (Hub): The final target hub.
        """
        self.id = f"D{id}"
        self.state = Drone_States.ASLEEP
        self.curr_hub = start_hub
        self.x = start_hub.x
        self.y = start_hub.y
        self.destination = end_hub
        self.idle = 0

    def move(self, next: Hub, conn: Connection) -> None:
        """Moves drone from current hub to adjacent hub via connection.

        Updates node occupancy counts, connection usage counters, and
        drone coordinates.

        Args:
            next (Hub): Target destination hub.
            conn (Connection): Connection used to transition hubs.
        """
        self.curr_hub.curr_drones -= 1
        next.curr_drones += 1
        conn.curr_link += 1
        self.curr_hub = next
        self.x = next.x
        self.y = next.y

    def path_find(self, map: Graph) -> None:
        """Calculates and stores optimal path from graph start to destination.

        Args:
            map (Graph): Graph instance providing pathfinding retrace logic.
        """
        self.path = map.retrace_steps(map.end)

    def en_route(self, target: Hub, conn: Connection) -> None:
        """Toggles or advances en-route state and updates location metrics.

        If not currently en route, enters en-route state and departs current
        hub. If already en route, completes traversal and arrives at
        target hub.

        Args:
            target (Hub): Target hub being traveled to.
            conn (Connection): Connection being traversed.
        """
        if self.state != Drone_States.EN_ROUTE:
            self.state = Drone_States.EN_ROUTE
            self.curr_hub.curr_drones -= 1
            conn.curr_link += 1
        else:
            self.state = Drone_States.AT_HUB
            conn.curr_link -= 1
            target.curr_drones += 1
            self.x = target.x
            self.y = target.y
            self.curr_hub = target

    def go_to(self, next: Hub, conn: Connection) -> str | Blocked:
        """Attempts to move drone to next hub based on state and limits.

        Evaluates target hub capacity, link capacity, and restricted zone
        rules before executing movement or returning blockage status.

        Args:
            next (Hub): Next target hub in planned path.
            conn (Connection): Connection leading to target hub.

        Returns:
            str | Blocked: Movement description string on success, or a
            Blocked enum indicating why movement failed.
        """
        if self.state == Drone_States.EN_ROUTE:
            if next.curr_drones < next.max_drones:
                self.en_route(next, conn)
                return f"{self.id}-{next}"
        elif self.state == Drone_States.AT_HUB:
            if next.curr_drones < next.max_drones:
                if next.zone == "restricted":
                    if (conn.curr_link < conn.max_link and
                            conn.curr_link + next.curr_drones <
                            next.max_drones):
                        self.en_route(next, conn)
                        return (f"{self.id}-"
                                f"{conn.get_name(self.curr_hub, next)}")
                    else:
                        return Blocked.CONN_FULL
                else:
                    if (conn.curr_link < conn.max_link):
                        self.move(next, conn)
                        return f"{self.id}-{next}"
                    else:
                        return Blocked.CONN_FULL
        elif self.state == Drone_States.ASLEEP:
            if next.curr_drones < next.max_drones:
                if next.zone == "restricted":
                    if (conn.curr_link < conn.max_link and
                            conn.curr_link + next.curr_drones <
                            next.max_drones):
                        self.en_route(next, conn)
                        return (f"{self.id}-"
                                f"{conn.get_name(self.curr_hub, next)}")
                    else:
                        return Blocked.IS_ASLEEP
                else:
                    if (conn.curr_link < conn.max_link):
                        self.state = Drone_States.AT_HUB
                        self.move(next, conn)
                        return f"{self.id}-{next}"
                    else:
                        return Blocked.IS_ASLEEP
            else:
                return Blocked.IS_ASLEEP
        return Blocked.HUB_FULL
