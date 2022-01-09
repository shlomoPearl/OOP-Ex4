"""
@author AchiyaZigi
OOP - Ex4
Very simple GUI example for python client to communicates with the server and "play the game!"
"""
import math as m
import threading
import time as t
from concurrent.futures import thread
from types import SimpleNamespace
from client import Client
import json
from pygame import gfxdraw
import pygame
from pygame import *

# init pygame
from client_python.DiGraph import DiGraph
from client_python.GraphAlgo import GraphAlgo

WIDTH, HEIGHT = 1080, 720

# default port
PORT = 6666
# server host (default localhost 127.0.0.1)
HOST = '127.0.0.1'
pygame.init()

screen = display.set_mode((WIDTH, HEIGHT), depth=32, flags=RESIZABLE)
width = screen.get_width()
height = screen.get_height()
clock = pygame.time.Clock()
pygame.font.init()

client = Client()
client.start_connection(HOST, PORT)

# pokemons = client.get_pokemons()
# pokemons_obj = json.loads(pokemons, object_hook=lambda d: SimpleNamespace(**d))

# print(pokemons)

graph_json = client.get_graph()

FONT = pygame.font.SysFont('Arial', 20, bold=True)
# load the json string into SimpleNamespace Object

# def scale(data, min_screen, max_screen, min_data, max_data):
#     """
#     get the scaled data with proportions min_data, max_data
#     relative to min and max screen dimentions
#     """
#     return ((data - min_data) / (max_data - min_data)) * (max_screen - min_screen) + min_screen
#
#
# # decorate scale with the correct values
#
# def my_scale(data, x=False, y=False):
#     if x:
#         return scale(data, 50, screen.get_width() - 50, g.min_x, g.max_x)
#     if y:
#         return scale(data, 50, screen.get_height() - 50, g.min_y, g.max_y)


# print(pokemons)

graph_json = client.get_graph()

FONT = pygame.font.SysFont('Arial', 20, bold=True)
# load the json string into SimpleNamespace Object

graph_algo = GraphAlgo();
graph_algo.load_from_json(client.get_graph())
g = graph_algo.get_graph()

epsilon = 0.001


def distance(point1, point2):
    dx_squared = m.pow((point1[0] - point2[0]), 2)  # (delta x)^2
    dy_squared = m.pow((point1[1] - point2[1]), 2)  # (delta y)^2
    d = m.sqrt(dx_squared + dy_squared)
    return d


def area_of_triangle(point1, point2, point3):
    dist1 = distance(point1, point2)
    dist2 = distance(point2, point3)
    dist3 = distance(point3, point1)
    perimeter = dist1 + dist2 + dist3  # perimeter
    S = perimeter / 2
    return m.sqrt(S * (S - dist1) * (S - dist2) * (S - dist3))  # Heron's formula


def distance_of_point_from_edge(source, destination, point):
    src_pos = g.nodes[source].position[:-1]
    dest_pos = g.nodes[destination].position[:-1]
    area = area_of_triangle(src_pos, dest_pos, point)
    base = distance(src_pos, dest_pos)
    h = (2 * area) / base
    return h


def is_on_edge(position: tuple, type: int) -> int:
    for edge_tuple in g.edges:
        if distance_of_point_from_edge(edge_tuple[0], edge_tuple[1], position) < epsilon:
            if (edge_tuple[1] - edge_tuple[0]) * type > 0:  # ensures pokemon is placed on the right edge (direction-wise)
                return edge_tuple


def is_on_node(position: tuple) -> int:
    for node_key in g.nodes:
        node_pos_tuple = g.nodes[node_key].position[:-1]
        if distance(position, node_pos_tuple) <= epsilon:
            return node_key


# scale:

diff_x = g.max_x - g.min_x
diff_y = g.max_y - g.min_y
x_factor = (width - 200) / diff_x
y_factor = (height - 200) / diff_y
margine = 100

for key in g.nodes:
    x, y = g.nodes[key].position[:-1]
    g.nodes[key].position = (x - g.min_x), (y - g.min_y), 0

# def arrow_offsets(self, source, dest, r):
#     source_pos = self.g.nodes[source].position
#     dest_pos = self.g.nodes[dest].position
#     dy = dest_pos[1] - source_pos[1]
#     dx = dest_pos[0] - source_pos[0]
#     distance = math.sqrt(math.pow(dx, 2) + math.pow(dy, 2))
#     sin = dy / distance
#     cos = dx / distance
#     x_offset = r * cos
#     y_offset = r * sin
#     return x_offset, y_offset
#
#


radius = 15
num_of_agent = int(client.get_info().split(':')[10].split('}')[0])
print(num_of_agent)
for i in range(num_of_agent):
    client.add_agent(f'{{\"id\":{i}}}')


def gota_cathem_all(node_list, agent):
    if node_list is not None:
        for node in node_list:
            if agent.dest == -1:
                client.choose_next_edge('{"agent_id":' + str(agent.id) + ', "next_node_id":' + str(node) + '}')
    return


# this commnad starts the server - the game is running now
client.start()

"""
The code below should be improved significantly:
The GUI and the "algo" are mixed - refactoring using MVC design pattern is required.
"""

last_move_time = t.time()
# print(last_move_time)

while client.is_running() == 'true':

    agents = json.loads(client.get_agents(), object_hook=lambda d: SimpleNamespace(**d)).Agents
    agents = [agent.Agent for agent in agents]
    for a in agents:
        x, y, _ = a.pos.split(',')
        a.pos = float(x) - g.min_x, float(y) - g.min_y

    pokemons = json.loads(client.get_pokemons(), object_hook=lambda d: SimpleNamespace(**d)).Pokemons
    pokemons = [p.Pokemon for p in pokemons]
    for p in pokemons:
        x, y, _ = p.pos.split(',')
        p.pos = float(x) - g.min_x, float(y) - g.min_y

    # check events
    button_color = (180, 230, 230)
    font = pygame.font.SysFont('ComicSans', 25, bold=True)
    text_stop = font.render('Stop', True, button_color)

    move_counter = (client.get_info().split(':')[4]).split(',')[0]
    time_to_end = int(client.time_to_end()) / 1000
    text_move_counter = font.render(f'Move Counter: {move_counter}', True, button_color)
    if time_to_end > 10:
        text_time_to_end = font.render(f'Time to End: {time_to_end}', True, button_color)
    else:
        text_time_to_end = font.render(f'Time to End: {time_to_end}', True, 'red')

    time_to_end = format((float(client.time_to_end()) / 1000), ".1f")
    text_move_counter = font.render(f'Moves Counter: {move_counter}', True, button_color)
    text_time_to_end = font.render(f'Time to End: {time_to_end} sec', True, button_color)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit(0)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if 0 <= mouse[0] <= 68 and 0 <= mouse[1] <= 40:
                client.stop()

    # refresh surface
    screen.fill(Color(0, 0, 0))
    mouse = pygame.mouse.get_pos()

    # if mouse is hovered on a button it
    # changes to lighter shade
    if 0 <= mouse[0] <= 68 and 0 <= mouse[1] <= 40:
        pygame.draw.rect(screen, (170, 170, 170), [0, 0, 68, 40])
    else:
        pygame.draw.rect(screen, (100, 100, 100), [0, 0, 68, 40])

    pygame.draw.rect(screen, (100, 100, 100), [72, 0, 275, 40])
    pygame.draw.rect(screen, (100, 100, 100), [351, 0, 340, 40])

    # superimposing the text onto our button
    screen.blit(text_stop, (3, 3))
    screen.blit(text_move_counter, (80, 3))
    screen.blit(text_time_to_end, (356, 3))

    # draw nodes
    for node in g.nodes.values():
        x = node.position[0] * x_factor + margine
        y = node.position[1] * y_factor + margine

        # its just to get a nice antialiased circle
        gfxdraw.filled_circle(screen, int(x), int(y), radius, Color(64, 80, 174))
        gfxdraw.aacircle(screen, int(x), int(y), radius, Color(255, 255, 255))

        # draw the node id
        id_srf = FONT.render(str(node.key), True, Color(255, 255, 255))
        rect = id_srf.get_rect(center=(x, y))
        screen.blit(id_srf, rect)

    # draw edges
    for edge in g.edges:
        # find the edge nodes
        src = edge[0]
        dest = edge[1]

        # scaled positions
        src_x = g.nodes[src].position[0] * x_factor + margine
        src_y = g.nodes[src].position[1] * y_factor + margine
        dest_x = g.nodes[dest].position[0] * x_factor + margine
        dest_y = g.nodes[dest].position[1] * y_factor + margine

        # draw the line
        pygame.draw.line(screen, Color(61, 72, 126), (src_x, src_y), (dest_x, dest_y))

        # add arrow heads

    # draw agents
    for agent in agents:
        x = agent.pos[0] * x_factor + margine
        y = agent.pos[1] * y_factor + margine

        pygame.draw.circle(screen, Color(122, 61, 23), (x, y), 10)
        image = pygame.image.load(r'..\ash_new.jpg')
        screen.blit(image, (x - 20, y - 35))

    # draw pokemons
    for p in pokemons:

        x = p.pos[0] * x_factor + margine
        y = p.pos[1] * y_factor + margine

        pygame.draw.circle(screen, Color(0, 255, 255), (x, y), 10)
        image = pygame.image.load(r'..\pikachu_new.jpg')
        screen.blit(image, (x - 20, y - 20))

        # update screen changes
        display.update()

        # refresh rate
        clock.tick(60)

        # choose next edge
        for pokemon in pokemons:

            pok_type = int(pokemon.type)
            pokemon_edge = is_on_edge(pokemon.pos, pok_type)
            print(pokemon_edge)
            shortest_time = m.inf
            allocated_agent = agents[0]
            path = []

            for agent in agents:
                if agent.dest == -1:  # if agents isn't busy
                    agent_node_key = is_on_node(agent.pos)
                    print(agent_node_key)
                    currents_sp = graph_algo.shortest_path(agent_node_key, pokemon_edge[1])
                    currents_st = currents_sp[0] / agent.speed
                    if currents_st < shortest_time:
                        shortest_time = currents_st
                        path = currents_sp[1]
                        allocated_agent = agent
                    print(path)

        # new thread
        ash = threading.Thread(gota_cathem_all(path, allocated_agent))
        ash.start()

    time_from_last_move = t.time() - last_move_time

    if time_from_last_move >= 0.1:
        client.move()
        last_move_time = t.time()

# game over:
