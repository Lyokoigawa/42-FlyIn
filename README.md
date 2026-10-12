*This project has been created as part of the 42 curriculum by lyokoiga*
<br><br/>
<h1 align="center">💻Fly-in</h1>
<p align="center"><i>"We're soarin'! Fly-in'!"</i></p>

## 📌 Description

Fly-in is a project in python where we had to implement a pathfinding algorithm in order to move a fleet of drones through a set of different maps with various types of zones from start to end, in the least amount of moves possible and without them crashing into each other.

The map is composed of various hubs and connections, with each hub having its own values like how many drones can fit in the hub, which zone type it is, so on and so forth.

Zone types are as follows:

|Zone Type|Info|
|-----|-----|
|Normal|Takes 1 turn to move into. Default zone.|
|Restricted|Takes 2 turns to move into. Drones first move into and wait inside the connection between both hubs before moving into the hub.|
|Priority|Takes 1 turn to move into, is considered first before other hub types during pathfinding|
|Blocked|Blocked hub. Drones cannot move nor consider blocked hubs for pathfinding.|

The program would output a set of strings which detailed where each drone is, broken up by a newline.

For the pathfinding algorithm, I decided to use Dijkstra, which is a greedy algorithm, meant to find the shortest path between point A and point B. It goes through every neighbouring node, attributing a cost of movement to that node, which takes it's inherent value and adds it to the total amount it already took to get there. It will then go to the next node in the heap, prioritizing smaller total values, until it has visited every possible node.
I modified this algorithm a little bit so that when a drone can't move because the next hub in it's path is already full, it'll attempt to reroute from where it is, caring only about the current state of the board, and not about the other drones that will come eventually, meaning the algorithm is also myopic in nature. It does this by adding the number of current drones in any hubs it can reach by a value equal to a fraction of the total amount of drones.

I decided to not implement certain features that would make my algorithm a bit better, such as a better lookahead that way drones can make better informed decisions. This does mean the algorithm struggles with a larger amount of drones (I found out they tend to ping-pong a little bit between certain hubs, especially if they're close to the start hub) and maps with more paths, but it still manages to pathfind well enough where it's not that much of a problem in the long run, as it still allows drones to pathfind normally.

We could optionally include a visualizer for the program using pygame, in order to be able to see and examine each move carefully, which could get a little confusing if relying solely on the program's text output.
I did decide to use pygame for the project, implementing a small control scheme to help visualize each turn better. The map is represented by a graph of circular hubs, with lines connecting each of them, and each drone has its own little small-scope procedurally generated sprite which I managed to create by randomizing a couple of sprites, colors and expressions. Each hub and drone also have their names displayed next to them. I also managed to stack each drone ID depending on how many drones were in the hub at a time.

## ⌨️ Instructions

### Installation

In order to run the program you must first make sure to install the needed dependencies using `make` and `make install`. After that, a virtual environment called "flyin" will be created in the folder. Enter the venv using `source flyin/bin/activate`. Then, finally, use `make run` to run the program using the default values.

In order to run the program with other configurations, run the program using `python3 main.py --map=[Path to the map] --visual=1`

### Visualizer Controls

Left and right arrow keys to change steps in the simulation... That's it, really.

### Creating your own custom maps

|||
|-|-|
|#|Starting a line with this beings a comment. The line will not be considered when parsing the map|
|hub:|The resulting line will be a hub. It will require: `name`, `x`, `y` and optional `metadata` (ex: hub: long_hallway2 7 0 [color=yellow max_drones=5 zone=restricted])|
|connection:|The resulting line will be a connection. It will require: `hub1`-`hub2` and optional `metadata` (ex: connection: long_hallway1-short_hallway5 [max_link_capacity=2])|
|start_hub:|Same thing as the regular hub. Denotes where the start of the map will be.|
|end_hub:|Same thing as the regular hub. Denotes where the end of the map will be.|

Metadata is always written between square brackets '[]', and contain keyword and values as follows:

|Key|Value|Description|
|-|-|-|
|max_drones|int|Hubs only. Sets the maximum amount of drones a hub can contain.|
|color|str|Hubs only. Sets the color of the hub. Single word colors only. Refer to the src/consts.py file for a list of valid color names.|
|zone|str|Hubs only. Sets the type of the zone. Refer to the list above in the Description section for more information on zone types.|
|max_link_capacity|int|Connection only. Sets the amount of drones that can go through the connection. Mainly important for restricted zones.|

Maps need at least:
- `start_hub` and an `end_hub`.
- `connections` between hubs.
- A valid pathway connecting start_hub to end_hub

Other hubs are optional.

I have a couple of example test maps in my github if you'd like to check some of them out.
(https://github.com/Lyokoigawa/42-FlyIn)

## Resources

https://www.pygame.org/docs/

https://www.geeksforgeeks.org/dsa/dijkstras-shortest-path-algorithm-greedy-algo-7/

### 🤖 AI Usage

AI was used to:
- Help with understanding djikstra and heapq
- Help with simulation logic and drone rerouting
- Help with learning the pygame module
- Help with organizing the README and finding typos
