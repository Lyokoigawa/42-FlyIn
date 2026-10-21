class PathfindingException(Exception):
    """Exception raised when pathfinding algorithms fail to find valid path."""

    def __init__(self, message: str) -> None:
        """Initializes PathfindingException with an error message string.

        Args:
            message (str): Explanation of the pathfinding failure.
        """
        super().__init__(message)
