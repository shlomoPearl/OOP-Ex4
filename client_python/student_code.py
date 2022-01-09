import math
import math as m
import random
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
from DiGraph import DiGraph
from GraphAlgo import GraphAlgo

width_factor = 1.4
height_factor = 1.1
WIDTH, HEIGHT = 1080 * width_factor, 720 * height_factor

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
FONT = pygame.font.SysFont('ComicSans', 20, bold=True)

client = Client()
client.start_connection(HOST, PORT)

graph_json = client.get_graph()

graph_algo = GraphAlgo()
graph_algo.load_from_json(client.get_graph())
g = graph_algo.get_graph()

epsilon = 0.00000001
radius = 15

# scale factors:
current_width = screen.get_width()
current_height = screen.get_height()

diff_x = g.max_x - g.min_x
diff_y = g.max_y - g.min_y
x_factor = (current_width - 200) / diff_x
y_factor = (current_height - 200) / diff_y
margin = 100

for key in g.nodes:
    x, y = g.nodes[key].position[:-1]
    g.nodes[key].position = (x - g.min_x), (y - g.min_y), 0


def distance(point1, point2):
    dx_squared = m.pow((point1[0] - point2[0]), 2)  # (delta x)^2
    dy_squared = m.pow((point1[1] - point2[1]), 2)  # (delta y)^2
    d = m.sqrt(dx_squared + dy_squared)
    return d


def area_of_triangle(point1, point2, point3):
    a = distance(point1, point2)
    b = distance(point2, point3)
    c = distance(point3, point1)
    S = (a + b + c) / 2
    sq = S * (S - a) * (S - b) * (S - c)
    if sq > 0:
        return m.sqrt(sq)  # Heron's formula
    else:
        return 0.0


def distance_of_point_from_edge(source, destination, point):
    src_pos = g.nodes[source].position[:-1]
    dest_pos = g.nodes[destination].position[:-1]
    area = area_of_triangle(src_pos, dest_pos, point)
    base = distance(src_pos, dest_pos)
    h = (2 * area) / base
    return h


def is_on_edge(position: tuple, type: int) -> int:
    for edge_tuple in g.edges:
        if (edge_tuple[1] - edge_tuple[0]) * type > 0:  # edge is the same type of pokemon edge
            if distance_of_point_from_edge(edge_tuple[0], edge_tuple[1], position) < epsilon:
                return edge_tuple


def is_on_node(position: tuple) -> int:
    for node_key in g.nodes:
        node_pos_tuple = g.nodes[node_key].position[:-1]
        if distance(position, node_pos_tuple) <= epsilon:
            return node_key


# def text_scale(text, font):
#     text_surface = font.render(text, True, (180, 230, 230)).convert_alpha()
#     cur_w, cur_h = screen.get_size()
#     txt_w, txt_h = text_surface.get_size()
#     text_surface = pygame.transform.smoothscale(text_surface, (txt_w * cur_w // width, txt_h * cur_h // height))
#
#     return text_surface, text_surface.get_rect()


def arrow_offsets(source, dest, r):
    source_pos = g.nodes[source].position
    dest_pos = g.nodes[dest].position
    dy = dest_pos[1] - source_pos[1]
    dx = dest_pos[0] - source_pos[0]
    distance = m.sqrt(m.pow(dx, 2) + m.pow(dy, 2))
    sin = dy / distance
    cos = dx / distance
    x_offset = r * cos
    y_offset = r * sin
    return x_offset, y_offset


def draw_arrow(start, end):
    rotation = m.degrees(
        m.atan2(start[1] - end[1], end[0] - start[0])) + 90
    arrow_size = 7
    pygame.draw.polygon(screen, Color('dark slate grey'), (
        (end[0] + arrow_size * m.sin(m.radians(rotation)), end[1] + arrow_size * m.cos(m.radians(rotation))),
        (end[0] + arrow_size * m.sin(m.radians(rotation - 120)),
         end[1] + arrow_size * m.cos(m.radians(rotation - 120))),
        (end[0] + arrow_size * m.sin(m.radians(rotation + 120)),
         end[1] + arrow_size * m.cos(m.radians(rotation + 120)))))

def draw_edges():
    # draw edges
    for edge in g.edges:
        # find the edge nodes
        src = edge[0]
        dest = edge[1]

        # scaled positions
        src_x = g.nodes[src].position[0] * x_factor + margin
        src_y = g.nodes[src].position[1] * y_factor + margin
        dest_x = g.nodes[dest].position[0] * x_factor + margin
        dest_y = g.nodes[dest].position[1] * y_factor + margin

        # draw the line with arrow
        x_offset, y_offset = arrow_offsets(src, dest, radius + 7)
        pygame.draw.line(screen, Color('dark slate grey'), (src_x + x_offset, src_y + y_offset),
                         (dest_x - x_offset, dest_y - y_offset))
        draw_arrow((src_x + x_offset, src_y + y_offset), (dest_x - x_offset, dest_y - y_offset))

def draw_nodes():
    # draw nodes
    for node in g.nodes.values():
        x = node.position[0] * x_factor + margin
        y = node.position[1] * y_factor + margin

        # its just to get a nice antialiased circle
        gfxdraw.filled_circle(screen, int(x), int(y), radius, Color('lawn green'))
        gfxdraw.aacircle(screen, int(x), int(y), radius, Color(0, 0, 0))

        # draw the node id
        id_srf = FONT.render(str(node.key), True, Color(0, 0, 0))
        rect = id_srf.get_rect(center=(x, y))
        screen.blit(id_srf, rect)

def draw_pokemons():
    for p in pokemons:
        x = p.pos[0] * x_factor + margin
        y = p.pos[1] * y_factor + margin

        pygame.draw.circle(screen, Color(0, 255, 255), (x, y), 10)
        image = pygame.image.load(r'..\pikachu_new.jpg')
        screen.blit(image, (x - 20, y - 20))

def draw_agents():
    for agent in agents:
        x = agent.pos[0] * x_factor + margin
        y = agent.pos[1] * y_factor + margin

        pygame.draw.circle(screen, Color(122, 61, 23), (x, y), 10)
        image = pygame.image.load(r'..\ash_new.jpg')
        screen.blit(image, (x - 20, y - 35))


info = json.loads(client.get_info())["GameServer"]
number_of_agents = int(info["agents"])

pokemons = json.loads(client.get_pokemons(), object_hook=lambda d: SimpleNamespace(**d)).Pokemons
pokemons = sorted([p.Pokemon for p in pokemons], key=lambda p: int(p.value), reverse=True)

for p in pokemons:
    x, y, _ = p.pos.split(',')
    p.pos = float(x) - g.min_x, float(y) - g.min_y
    pokemon_edge = is_on_edge(p.pos, p.type)
    # print(pokemon_edge)
    for i in range(number_of_agents):
        client.add_agent('{"id":' + str(pokemon_edge[0]) + "}")


def gota_cathem_all(node_list, agent):
    if node_list is not None:
        for node in node_list:
            if agent.dest == -1:
                client.choose_next_edge('{"agent_id":' + str(agent.id) + ', "next_node_id":' + str(node) + '}')
    return

def choose_next_node_algo():
# choose next edge
    for pokemon in pokemons:
        allocated_agent = agents[0]
        path = []
        pok_type = int(pokemon.type)
        pokemon_edge = is_on_edge(pokemon.pos, pok_type)
        shortest_time = m.inf
        ash = threading.Thread()
        for agent in agents:
            if agent.dest == -1 and not ash.is_alive():  # if agents isn't busy
                agent_node_key = is_on_node(agent.pos)
                currents_sp = graph_algo.shortest_path(agent_node_key, pokemon_edge[0])
                currents_st = currents_sp[0] / agent.speed
                if currents_st < shortest_time:
                    shortest_time = currents_st
                    path = currents_sp[1] + [pokemon_edge[1]]
                    # print(path)
                    allocated_agent = agent
                ash.__init__(gota_cathem_all(path, allocated_agent))
                ash.start()
        # new thread

# this commnad starts the server - the game is running now
client.start()

last_move_time = t.time()

while client.is_running() == 'true':

    agents = json.loads(client.get_agents(), object_hook=lambda d: SimpleNamespace(**d)).Agents
    agents = [agent.Agent for agent in agents]
    for a in agents:
        x, y, _ = a.pos.split(',')
        a.pos = float(x) - g.min_x, float(y) - g.min_y

    pokemons = json.loads(client.get_pokemons(), object_hook=lambda d: SimpleNamespace(**d)).Pokemons
    pokemons = sorted([p.Pokemon for p in pokemons], key=lambda p: int(p.value), reverse=True)
    for p in pokemons:
        x, y, _ = p.pos.split(',')
        p.pos = float(x) - g.min_x, float(y) - g.min_y

    font_percent = int(((3.571 * current_height) // 100 + (2.314 * current_width) // 100) / 2)
    # font_percent = int(25 * current_height / 720)

    button_color = (180, 230, 230)
    font = pygame.font.SysFont('ComicSans', font_percent, bold=True, )
    text_stop = font.render('Stop', True, button_color)

    time_to_end = format((float(client.time_to_end()) / 1000), ".1f")
    move_counter = (client.get_info().split(':')[4]).split(',')[0]
    grade = int(client.get_info().split(':')[5].split(',')[0])
    text_move_counter = font.render(f'Move Counter: {move_counter}', True, button_color)
    text_grade = font.render(f'Grade: {grade}', True, button_color)
    if float(time_to_end) > 10:
        text_time_to_end = font.render(f'Time to End: {time_to_end} sec', True, button_color)
    else:
        text_time_to_end = font.render(f'Time to End: {time_to_end} sec', True, 'red')

    y_percent = (5.7 * current_height) // 100
    stop_x_percent = (6.3 * current_width) // 100
    move_x_percent = (29 * current_width) // 100
    time_x_percent = (58 * current_width) // 100
    grade_x_percent = (72 * current_width) // 100
    offset_percent = (0.37 * current_width) // 100 + 1

    # refresh surface
    screen.fill('light grey')
    mouse = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit(0)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if 0 <= mouse[0] <= stop_x_percent and 0 <= mouse[1] <= y_percent:
                client.stop()

    # if mouse is hovered on a button it
    # changes to lighter shade
    if 0 <= mouse[0] <= 68 and 0 <= mouse[1] <= 40:
        pygame.draw.rect(screen, (170, 170, 170), [offset_percent, offset_percent, stop_x_percent, y_percent])
    else:
        pygame.draw.rect(screen, (100, 100, 100), [offset_percent, offset_percent, stop_x_percent, y_percent])
    # draw button for number of moves
    pygame.draw.rect(screen, (100, 100, 100),
                     [stop_x_percent + 2 * offset_percent, offset_percent, move_x_percent - (stop_x_percent + offset_percent),
                      y_percent])
    # draw button for time to end
    pygame.draw.rect(screen, (100, 100, 100),
                     [move_x_percent + 2 * offset_percent, offset_percent, time_x_percent - move_x_percent,
                      y_percent])
    # draw button for grade
    pygame.draw.rect(screen, (100, 100, 100),
                     [time_x_percent + 3 * offset_percent, offset_percent, grade_x_percent - (time_x_percent - offset_percent),
                      y_percent])

    # superimposing the text onto our button
    text_y_percent = (0.3 * current_width) // 100 + 1

    screen.blit(text_stop, (text_y_percent + 2 * offset_percent, text_y_percent))
    screen.blit(text_move_counter, (stop_x_percent + text_y_percent + 3 * offset_percent, text_y_percent))
    screen.blit(text_time_to_end, (move_x_percent + text_y_percent + 3 * offset_percent, text_y_percent))
    screen.blit(text_grade, (time_x_percent + text_y_percent + offset_percent * 4, text_y_percent))

    draw_edges()
    draw_nodes()
    draw_pokemons()
    draw_agents()

    # update screen changes
    display.update()

    # refresh rate
    clock.tick(60)

    choose_next_node_algo()

    # clock moves in-order to stay under 10 moves a second
    time_from_last_move = t.time() - last_move_time

    if time_from_last_move >= 0.095:
        client.move()
        last_move_time = t.time()

# game over:
