import pygame
import random
import math
from .map import Hub
from .consts import COLOR_HEX, TAGLINES, DRONE_COLORS, DRONE_EYES
from .graph import Graph
from collections.abc import Iterable


class Visual_Hub:
    def __init__(self, name: str, hub: Hub) -> None:
        self.hub = hub
        self.name = name

    def load_sprite(self, size: float) -> None:
        self.base = pygame.Surface((64, 64), pygame.SRCALPHA)
        if self.hub.color == "rainbow":
            self.body = pygame.image.load("assets/hub/hub/rainbow_hub.png")
        else:
            self.body = pygame.image.load("assets/hub/hub/hub.png")
            self.calc_color()
            self.body.fill(self.color, special_flags=pygame.BLEND_MULT)
        if self.hub.zone == "blocked":
            self.border = pygame.image.load("assets/hub/border/blocked_border.png")
        elif self.hub.zone == "restricted":
            self.border = pygame.image.load("assets/hub/border/restricted_border.png")
        elif self.hub.zone == "normal":
            self.border = pygame.image.load("assets/hub/border/normal_border.png")
        else:
            self.border = None
        self.base.blit(self.body, (0, 0))
        if self.border is not None:
            self.base.blit(self.border, (0, 0))
        self.sprite = pygame.transform.scale(self.base,
                                             self.calc_scale(size))

    def calc_pos(self, width: float, height: float,
                 margin: float, pos: dict[str, int]) -> None:
        if pos["min_x"] == pos["max_x"]:
            fra_x = 0.5
        else:
            fra_x = (self.hub.x - pos["min_x"]) / (pos["max_x"] - pos["min_x"])
        if pos["min_y"] == pos["max_y"]:
            fra_y = 0.5
        else:
            fra_y = (self.hub.y - pos["min_y"]) / (pos["max_y"] - pos["min_y"])
        self.x = (fra_x * (width - 2 * margin)) + margin
        self.y = (fra_y * (height - 2 * margin)) + margin
        self.center = [self.x, self.y]

    def calc_color(self) -> None:
        raw_color = self.hub.color
        hex = COLOR_HEX[raw_color].strip("#")
        rgb = [int(hex[i:i + 2], 16) for i in (0, 2, 4)]
        self.color = rgb

    def sprite_pos(self) -> list[float]:
        sprite_x = self.x - (self.sprite.get_width() / 2)
        sprite_y = self.y - (self.sprite.get_height() / 2)
        return [sprite_x, sprite_y]

    def calc_scale(self, size: float) -> list[float]:
        width = size * 2.5
        height = size * 2.5
        return [width, height]

    def name_pos(self, size: float, surface: pygame.Surface) -> list[float]:
        name_x = self.x - (surface.get_width() / 2)
        name_y = self.y - (surface.get_height() + (size * 2))
        return [name_x, name_y]


class Visual_Drone:
    def __init__(self, id: str, hub: Visual_Hub) -> None:
        self.id = id
        self.x = hub.x
        self.y = hub.y
        self.center = [self.x, self.y]
        self.color = DRONE_COLORS[random.randint(0, len(DRONE_COLORS) - 1)]
        self.target_x = self.x
        self.target_y = self.y

    def load_sprite(self, size: float) -> None:
        self.base = pygame.Surface((64, 64), pygame.SRCALPHA)
        self.body = pygame.image.load("assets/drone/drone_base.png")
        eyes = DRONE_EYES[random.randint(0, len(DRONE_EYES) - 1)]
        self.eyes = pygame.image.load(f"assets/drone/eyes/{eyes}")
        self.base.blit(self.body, (0, 0))
        self.base.blit(self.eyes, (0, 0))
        self.base.fill(self.color, special_flags=pygame.BLEND_MULT)
        self.sprite = pygame.transform.scale(self.base,
                                             self.calc_scale(size))

    def target(self, x: float, y: float) -> None:
        self.target_x = x
        self.target_y = y

    def update_pos(self, hub: list[float]) -> None:
        self.x = hub[0]
        self.y = hub[1]
        self.center = [self.x, self.y]

    def move(self) -> None:
        self.x = lerp(self.x, self.target_x, 0.1)
        self.y = lerp(self.y, self.target_y, 0.1)
        self.center = [self.x, self.y]

    def reached(self) -> bool:
        check = 0
        result = False
        if self.x > (self.target_x * 0.99) and self.x < (self.target_x * 1.01):
            check += 1
        if self.y > (self.target_y * 0.99) and self.y < (self.target_y * 1.01):
            check += 1
        if check == 2:
            result = True
        return result

    def sprite_pos(self) -> list[float]:
        sprite_x = self.x - (self.sprite.get_width() / 2)
        sprite_y = self.y - (self.sprite.get_height() / 2)
        return [sprite_x, sprite_y]

    def calc_scale(self, size: float) -> list[float]:
        width = size * 3
        height = size * 3
        return [width, height]

    def name_pos(self, size: float,
                 surface: pygame.Surface,
                 offset: int) -> list[float]:
        real_offset = offset * surface.get_height()
        name_x = self.x - (surface.get_width() / 2)
        name_y = self.y + (surface.get_height() + size) + real_offset
        return [name_x, name_y]


def hub_drone_count(turn: dict[str, str]) -> dict[str, list[str]]:
    hubs = {hub: list() for hub in turn.values()}
    for drone, hub in turn.items():
        hubs[hub].append(drone)
    return hubs


def drone_finder(hubs: dict[str, list[str]], id: str) -> int:
    for hub in hubs.values():
        if id in hub:
            return hub.index(id)
    return 0


def min_max(hubs: Iterable[Hub]) -> dict[str, int]:
    xs = [hub.x for hub in hubs]
    ys = [hub.y for hub in hubs]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    pos: dict[str, int] = {"min_x": min_x,
                           "min_y": min_y,
                           "max_x": max_x,
                           "max_y": max_y}
    return pos


def lerp(start: float, end: float, t: float) -> float:
    return start + (end - start) * t


def calc_size(width: float, height: float, hubs: int) -> float:
    area = width * height
    size = (math.sqrt(area / hubs)) / 10
    if size < 1:
        size = 1
    return size


def find_hub(to_find: str, hubs: list[Visual_Hub]) -> Visual_Hub:
    for hub in hubs:
        if hub.name == to_find:
            to_return = hub
    return to_return


def connection_center(conn: str, v_hubs: list[Visual_Hub]) -> list[float]:
    connection = conn.split("-")
    hub_1 = find_hub(connection[0], v_hubs)
    hub_2 = find_hub(connection[1], v_hubs)
    mid_x = lerp(hub_1.x, hub_2.x, 0.5)
    mid_y = lerp(hub_1.y, hub_2.y, 0.5)
    return [mid_x, mid_y]


def run(map: Graph, history: list[dict[str, str]]) -> None:
    pygame.init()
    clock = pygame.time.Clock()
    info = pygame.display.Info()
    screen = pygame.display.set_mode((info.current_w, info.current_h),
                                     pygame.RESIZABLE)
    tagline = TAGLINES[random.randint(0, len(TAGLINES) - 1)]
    pygame.display.set_caption(f"Flyin - {tagline}")

    turn = 0
    pos = min_max(map.hubs.values())
    size = calc_size(info.current_w, info.current_h, len(map.hubs))
    font = pygame.font.SysFont(None, int(size) - 1)
    max_drone_text = font.render(". . .", True, [0, 0, 0])
    v_hubs: list[Visual_Hub] = []
    for name, hub in map.hubs.items():
        n_hub = Visual_Hub(name, hub)
        n_hub.calc_pos(info.current_w, info.current_h, size * 3, pos)
        n_hub.load_sprite(size)
        v_hubs.append(n_hub)
    v_drones: list[Visual_Drone] = []
    for drone, hub_name in history[turn].items():
        hub = find_hub(hub_name, v_hubs)
        n_drone = Visual_Drone(drone, hub)
        n_drone.load_sprite(size)
        v_drones.append(n_drone)

    running = True
    while running:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.VIDEORESIZE:
                size = calc_size(event.w, event.h, len(v_hubs))
                for v_hub in v_hubs:
                    scale = v_hub.calc_scale(size)
                    v_hub.calc_pos(event.w, event.h, size * 3, pos)
                    v_hub.sprite = pygame.transform.scale(v_hub.base,
                                                          scale)
                for v_drone in v_drones:
                    scale = v_drone.calc_scale(size)
                    hub = history[turn][v_drone.id]
                    if "-" in hub:
                        hub = connection_center(hub, v_hubs)
                    else:
                        hub = find_hub(hub, v_hubs).center
                    v_drone.target(hub[0], hub[1])
                    v_drone.sprite = pygame.transform.scale(v_drone.base,
                                                            scale)
                font = pygame.font.SysFont(None, int(size) - 1)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and turn > 0:
                    turn -= 1
                    for v_drone in v_drones:
                        next_hub = history[turn][v_drone.id]
                        if "-" in next_hub:
                            target_hub = connection_center(next_hub,
                                                           v_hubs)
                        else:
                            target_hub = find_hub(next_hub, v_hubs).center
                        v_drone.target(target_hub[0], target_hub[1])
                elif event.key == pygame.K_RIGHT and turn < len(history) - 1:
                    turn += 1
                    for v_drone in v_drones:
                        next_hub = history[turn][v_drone.id]
                        if "-" in next_hub:
                            target_hub = connection_center(next_hub,
                                                           v_hubs)
                        else:
                            target_hub = find_hub(next_hub, v_hubs).center
                        v_drone.target(target_hub[0], target_hub[1])
        screen.fill((30, 30, 60))
        line = int(size / 10)
        if line < 1:
            line = 1
        d_prints = hub_drone_count(history[turn])
        for conn in map.connections:
            points = [v_hub for v_hub in v_hubs if v_hub.hub in conn]
            pygame.draw.line(screen, [255, 255, 255],
                             points[0].center,
                             points[1].center,
                             line)
        for v_hub in v_hubs:
            hub_text = font.render(v_hub.name, True, [0, 0, 0])
            screen.blit(v_hub.sprite, v_hub.sprite_pos())
            screen.blit(hub_text, v_hub.name_pos(size, hub_text))
        for v_drone in v_drones:
            drone_text = font.render(v_drone.id, True, [0, 0, 0])
            # pygame.draw.circle(screen, v_drone.color, v_drone.center, size * 0.9)
            screen.blit(v_drone.sprite, v_drone.sprite_pos())
            if v_drone.reached():
                v_drone.update_pos([v_drone.target_x, v_drone.target_y])
            else:
                v_drone.move()
            text_offset = drone_finder(d_prints, v_drone.id)
            if text_offset >= 5:
                text_offset = 5
                screen.blit(max_drone_text,
                            v_drone.name_pos(size * 0.9,
                                             max_drone_text,
                                             text_offset))
            else:
                screen.blit(drone_text,
                            v_drone.name_pos(size * 0.9,
                                             drone_text,
                                             text_offset))
        pygame.display.flip()

    pygame.quit()
