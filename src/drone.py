from enum import Enum
from .map import Hub, Connection
from .graph import Graph


class Drone_States(Enum):
    AT_HUB = "at_hub"
    EN_ROUTE = "en_route"
    ASLEEP = "asleep"


class Blocked(Enum):
    HUB_FULL = "hub_full"
    CONN_FULL = "conn_full"
    IS_ASLEEP = "is_asleep"


class DroneSystem:
    def __init__(self, nb_drones: int, map: Graph) -> None:
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
        print()
        print(f"Total turns: {dro.turns}")
        return history


class Drone:
    def __init__(self, id: int, start_hub: Hub, end_hub: Hub) -> None:
        self.id = f"D{id}"
        self.state = Drone_States.ASLEEP
        self.curr_hub = start_hub
        self.x = start_hub.x
        self.y = start_hub.y
        self.destination = end_hub
        self.idle = 0

    def move(self, next: Hub) -> None:
        self.curr_hub.curr_drones -= 1
        next.curr_drones += 1
        self.curr_hub = next
        self.x = next.x
        self.y = next.y

    def path_find(self, map: Graph) -> None:
        self.path = map.retrace_steps(map.end)

    def en_route(self, target: Hub, conn: Connection) -> None:
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
                        return f"{self.id}-{conn.get_name(self.curr_hub,
                                                          next)}"
                    else:
                        return Blocked.CONN_FULL
                else:
                    self.move(next)
                    return f"{self.id}-{next}"
        elif self.state == Drone_States.ASLEEP:
            if next.curr_drones < next.max_drones:
                if next.zone == "restricted":
                    if (conn.curr_link < conn.max_link and
                            conn.curr_link + next.curr_drones <
                            next.max_drones):
                        self.en_route(next, conn)
                        return f"{self.id}-{conn.get_name(self.curr_hub,
                                                          next)}"
                    else:
                        return Blocked.IS_ASLEEP
                else:
                    self.state = Drone_States.AT_HUB
                    self.move(next)
                    return f"{self.id}-{next}"
            else:
                return Blocked.IS_ASLEEP
        return Blocked.HUB_FULL
