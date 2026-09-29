from enum import Enum
from typing import Any
from .colors import paint_text


class Hub_Types(Enum):
    HUB = "hub"
    START_HUB = "start_hub"
    END_HUB = "end_hub"


class Hub:
    def __init__(self, type: str, name: str, x: int, y: int, n: int = 1):
        self.type = Hub_Types(type)
        self.name = name
        self.x = x
        self.y = y
        self.curr_drones = 0
        if self.type == Hub_Types.HUB:
            self.max_drones = 1
        else:
            self.max_drones = n
        self.zone = "normal"
        self.color = "white"

    def __str__(self) -> str:
        return paint_text(self.name, self.color)

    def set_meta(self, metadata: dict[str, Any]) -> None:
        for k, v in metadata.items():
            if k == "max_drones":
                self.max_drones = v
            if k == "zone":
                self.zone = v
            if k == "color":
                self.color = v

    def drone_reached(self) -> None:
        self.curr_drones += 1

    def drone_left(self) -> None:
        self.curr_drones -= 1


class Connection:
    def __init__(self, hub1: Hub, hub2: Hub) -> None:
        self.hub1 = hub1
        self.hub2 = hub2
        self.curr_link = 0
        self.max_link = 1
        self.hubs = [hub1, hub2]

    def __contains__(self, hub: Hub) -> bool:
        if hub == self.hub1 or hub == self.hub2:
            return True
        return False

    def __str__(self) -> str:
        return f"{self.hub1.name}-{self.hub2.name}"

    def get_name(self, src: Hub, dest: Hub) -> str:
        if src == self.hub1:
            return f"{self.hub1}-{self.hub2}"
        return f"{self.hub2}-{self.hub1}"

    def set_meta(self, metadata: int) -> None:
        self.max_link = metadata

    def drone_reached(self) -> None:
        self.curr_link += 1

    def drone_left(self) -> None:
        self.curr_link -= 1
