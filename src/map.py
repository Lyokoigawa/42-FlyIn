from enum import Enum
from typing import Any
from .colors import paint_text


class Hub_Types(Enum):
    """Categorizes the role of a hub within the graph network."""

    HUB = "hub"
    START_HUB = "start_hub"
    END_HUB = "end_hub"


class Hub:
    """Represents a hub node within the navigation graph map.

    Tracks capacity limits, current occupancy, spatial coordinates,
    and metadata attributes such as zone types and display colors.

    Attributes:
        type (Hub_Types): Classification role of the hub.
        name (str): Unique name identifier.
        x (int): Spatial x-coordinate position.
        y (int): Spatial y-coordinate position.
        curr_drones (int): Count of drones currently located at this hub.
        max_drones (int): Maximum drone capacity threshold for this hub.
        zone (str): Zone status string ('normal', 'restricted', etc.).
        color (str): Display color identifier used for text and sprite
            rendering.
    """

    def __init__(self, type: str, name: str, x: int, y: int, n: int = 1):
        """Initializes a Hub instance with location, type, and capacity.

        Args:
            type (str): Type string matching a Hub_Types enum value.
            name (str): Identifier name for the hub.
            x (int): Spatial x-coordinate.
            y (int): Spatial y-coordinate.
            n (int, optional): Initial drone capacity for non-standard hubs.
                Defaults to 1.
        """
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
        """Returns the hub's name wrapped in ANSI color escape codes.

        Returns:
            str: Colorized name string.
        """
        return paint_text(self.name, self.color)

    def set_meta(self, metadata: dict[str, Any]) -> None:
        """Updates hub attributes based on a metadata dictionary.

        Args:
            metadata (dict[str, Any]): Dictionary containing metadata key-value
                pairs like 'max_drones', 'zone', or 'color'.
        """
        for k, v in metadata.items():
            if k == "max_drones":
                self.max_drones = v
            if k == "zone":
                self.zone = v
            if k == "color":
                self.color = v

    def drone_reached(self) -> None:
        """Increments the current drone occupancy count by 1."""
        self.curr_drones += 1

    def drone_left(self) -> None:
        """Decrements the current drone occupancy count by 1."""
        self.curr_drones -= 1


class Connection:
    """Represents an edge path connecting two hubs in the graph network.

    Tracks current link traffic utilization and maximum capacity limits.

    Attributes:
        hub1 (Hub): Primary endpoint hub instance.
        hub2 (Hub): Secondary endpoint hub instance.
        curr_link (int): Number of drones currently traversing this connection.
        max_link (int): Maximum simultaneous drone capacity threshold.
        hubs (list[Hub]): List containing both endpoint hub instances.
    """

    def __init__(self, hub1: Hub, hub2: Hub) -> None:
        """Initializes a Connection instance between two hub endpoints.

        Args:
            hub1 (Hub): First endpoint hub.
            hub2 (Hub): Second endpoint hub.
        """
        self.hub1 = hub1
        self.hub2 = hub2
        self.curr_link = 0
        self.max_link = 1
        self.hubs = [hub1, hub2]

    def __contains__(self, hub: Hub) -> bool:
        """Checks if a given hub is an endpoint of this connection.

        Args:
            hub (Hub): Hub instance to check.

        Returns:
            bool: True if hub is either hub1 or hub2, False otherwise.
        """
        if hub == self.hub1 or hub == self.hub2:
            return True
        return False

    def __str__(self) -> str:
        """Returns string representation formatted as 'Hub1Name-Hub2Name'.

        Returns:
            str: Connection endpoint name string.
        """
        return f"{self.hub1.name}-{self.hub2.name}"

    def get_name(self, src: Hub, dest: Hub) -> str:
        """Returns connection string relative to traversal direction.

        Args:
            src (Hub): Source departure hub.
            dest (Hub): Target arrival hub.

        Returns:
            str: Directional path name string.
        """
        if src == self.hub1:
            return f"{self.hub1}-{self.hub2}"
        return f"{self.hub2}-{self.hub1}"

    def set_meta(self, metadata: int) -> None:
        """Sets the maximum link capacity limit for this connection.

        Args:
            metadata (int): Maximum link capacity limit value.
        """
        self.max_link = metadata

    def drone_reached(self) -> None:
        """Increments current link traffic count by 1."""
        self.curr_link += 1

    def drone_left(self) -> None:
        """Decrements current link traffic count by 1."""
        self.curr_link -= 1
