"""Global constants and configuration lookup tables for the Drone Visualizer.

This module provides hex color values, random taglines, sprite assets,
and RGB drone color palettes.
"""

COLOR_HEX: dict[str, str] = {
    "red": "#FF0000",
    "yellow": "#FFFF00",
    "blue": "#0000FF",
    "orange": "#FF9900",
    "green": "#00FF00",
    "purple": "#9900FF",
    "white": "#FFFFFF",
    "gray": "#888888",
    "black": "#000000",
    "cyan": "#00CCFF",
    "brown": "#7B3F00",
    "lime": "#5DFD00",
    "magenta": "#FF00FF",
    "gold": "#A1A100",
    "maroon": "#800000",
    "darkred": "#AD0000",
    "crimson": "#B22222",
    "violet": "#6A006A",
    "hotpink": "#FF00AA",
    "pink": "#FF55CC",
    "softpink": "#FFAADD",
    "lightblue": "#00AAFF",
    "rainbow": "special"
}


TAGLINES: list[str] = [
    "Letting drones fly since 1917",
    "Also try: A-maze-ing!",
    "Pathfinding into your heart",
    "Visualizer",
    "Moulinette? Who's that?",
    "Python6.7",
    "Please help I'm on pace 24",
    "PLEASE EVALUATOR I NEED THIS",
    "wow",
    "yippee! they fly!",
    "Please don't crash",
    "I love you",
    "                 ",
    "1994732207135885729",
    "Lillia's favourite project so far.",
    "Whoopsie! You weren't supposed to see that...",
    "Soarin~ Flyin~"
]


DRONE_EYES: list[str] = [
    "eyes_bored.png",
    "eyes_determined.png",
    "eyes_glad.png",
    "eyes_sly.png",
    "eyes_surprised.png",
]


DRONE_COLORS: list[list[int]] = [
    [255, 144, 162],
    [88, 255, 165],
    [127, 55, 255],
    [33, 255, 249],
    [255, 121, 198]
]
