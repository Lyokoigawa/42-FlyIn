from .consts import COLOR_HEX as colors


def paint_text(text: str, color: str) -> str:
    """Applies ANSI escape sequences to colorize text for terminal output.

    Converts a color name into RGB values from a global color lookup table and
    wraps the given string in ANSI escape codes. Supports single colors as well
    as a special 'rainbow' cycle applied character by character.

    Args:
        text (str): String content to colorize.
        color (str): Color identifier matching a key in the `colors` dict,
            or 'rainbow' to cycle through rainbow ANSI colors.

    Returns:
        str: ANSI-escaped string that renders with the chosen color(s) when
        printed to a terminal.
    """
    if color != "rainbow":
        hex = colors[color].strip("#")
        rgb = [int(hex[i:i + 2], 16) for i in (0, 2, 4)]
        r, g, b = rgb
        return f"\x1b[38;2;{r};{g};{b}m{text}\x1b[0m"
    else:
        rainbow = ["\x1b[38;2;255;0;0m",
                   "\x1b[38;2;255;145;0m",
                   "\x1b[38;2;255;255;0m",
                   "\x1b[38;2;0;150;255m",
                   "\x1b[38;2;0;0;255m",
                   "\x1b[38;2;150;0;255m",
                   "\x1b[38;2;255;0;215m"]
        i = 0
        n_text = ""
        while i < len(text):
            for c in rainbow:
                if i >= len(text):
                    break
                n_text += f"{c}{text[i]}"
                i += 1
        n_text += "\x1b[0m"
        return n_text
