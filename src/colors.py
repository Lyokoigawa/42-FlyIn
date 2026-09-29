from .consts import COLOR_HEX as colors


def paint_text(text: str, color: str) -> str:
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
