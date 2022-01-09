import json
import math
import copy
import tkinter as tk
from typing import List
from client_python.DiGraph import DiGraph
from collections import deque
import random


class GraphAlgo:

    def __init__(self, graph: DiGraph = DiGraph()):
        self.g = graph

    """This abstract class represents an interface of a graph."""

    def get_graph(self) -> DiGraph:
        """
        :return: the directed graph on which the algorithm works on.
        """
        return self.g

    def load_from_json(self, json_string: str) -> bool:
        """
        Loads a graph from a json file.
        @param file_name: The path to the json file
        @returns True if the loading was successful, False o.w.
        """
        json_graph = json.loads(json_string)
        node_list = json_graph["Nodes"]
        edge_list = json_graph["Edges"]
        # iterate over node_list to save nodes to graph
        graph = DiGraph()
        for node in node_list:
            key = node["id"]
            graph.add_node(key, None)
            if "pos" in node:
                pos_string_list = node["pos"].split(",")
                # make stings of numbers into actual float variables:
                pos_tuple = float(pos_string_list[0]), float(pos_string_list[1]), float(pos_string_list[2])
                graph.nodes[key].position = pos_tuple
            else:
                graph.ensure_position(key)
            graph.update_min_max(key)

        # iterate over node_list to save nodes to graph
        for edge in edge_list:
            # iterate over node_list to save nodes to graph
            graph.add_edge(edge["src"], edge["dest"], edge["w"])
        self.g = graph
        return True

    def save_to_json(self, file_name: str) -> bool:
        """
        Saves the graph in JSON format to a file
        @param file_name: The path to the out file
        @return: True if the save was successful, False o.w.
        """
        if self.g is not None:
            # initialize lists
            node_list = []
            edge_list = []
            for node in self.g.nodes.values():
                node_dict = {}
                if node.position is not None:
                    pos_tuple = node.position
                    #  create dict with node parameters
                    # position is converted to string format
                    node_dict["pos"] = f"{pos_tuple[0]},{pos_tuple[1]},{pos_tuple[2]}"
                node_dict["id"] = node.key
                node_list.append(node_dict)  # add to node list
            for key, weight in self.g.edges.items():
                #  create dict with edge parameters according to format
                edge_dict = {"src": key[0], "w": weight, "dest": key[1]}
                edge_list.append(edge_dict)  # add to edge list
            graph_dict = {"Edges": edge_list, "Nodes": node_list}  # create final graph to be dumped
            with open(file_name, "w") as file:
                json.dump(graph_dict, file, indent=4)  # save to json file
            return True
        return False

    def shortest_path(self, id1: int, id2: int) -> (float, list):
        """
        Returns the shortest path from node id1 to node id2 using Dijkstra's Algorithm
        @param id1: The start node id
        @param id2: The end node id
        @return: The distance of the path, a list of the nodes ids that the path goes through
        Example:
    #      >>> from GraphAlgo import GraphAlgo
    #       >>> g_algo = GraphAlgo()
    #        >>> g_algo.addNode(0)
    #        >>> g_algo.addNode(1)
    #        >>> g_algo.addNode(2)
    #        >>> g_algo.addEdge(0,1,1)
    #        >>> g_algo.addEdge(1,2,4)
    #        >>> g_algo.shortestPath(0,1)
    #        (1, [0, 1])
    #        >>> g_algo.shortestPath(0,2)
    #        (5, [0, 1, 2])
        Notes:
        If there is no path between id1 and id2, or one of them dose not exist the function returns (float('inf'),[])
        More info:
        https://en.wikipedia.org/wiki/Dijkstra's_algorithm
        """
        unchecked_nodes = copy.copy(self.g.nodes)  # initialize list of unchecked nodes
        # zero the in-weight attribute of all the nodes
        for item in unchecked_nodes:
            unchecked_nodes[item].in_weight = math.inf
        unchecked_nodes[id1].in_weight = 0
        result = []  # initialize empty list (to be filled and returned)
        if id1 == id2:  # one node - no path
            return 0, [id1]
        while len(unchecked_nodes) > 0:
            # save the node with the minimum in-weight. this will change in the course of the loop
            current_key = min(unchecked_nodes.items(), key=lambda node_tuple: node_tuple[1].in_weight)[1].key
            unchecked_nodes.pop(current_key)  # remove and save node object
            for key in self.g.nodes[current_key].out_going_edges:  # iterate over current node's neighbours
                current_node = self.g.nodes[current_key]
                next_node = self.g.nodes[key]
                current_edge_weight = next_node.in_going_edges[current_key]
                if current_node.in_weight + current_edge_weight < next_node.in_weight:  # we have found a shorter path
                    next_node.in_weight = current_node.in_weight + current_edge_weight
                    next_node.prev_node_key = current_node.key  # set previous node attribute inorder to reverse
                    # engineer the path list

                    if key == id2:  # we have reached our destination node
                        result.clear()  # clear result because we may have found a shorter path to the destination
                        # so we'd like to reconstruct the list

                        # reconstructing list:
                        result.append(id2)
                        node = current_node
                        while node.key != id1:
                            result.insert(0, node.key)  # insert all prev nodes to the head of the list (left
                            # hand side)
                            node = self.g.nodes[node.prev_node_key]  # iterate
                        result.insert(0, id1)  # add source node
        distance = self.g.nodes[id2].in_weight
        return distance, result

    def max_shortest_path(self, source: int):
        unchecked_nodes = copy.copy(self.g.nodes)
        max_shortest_path = 0
        for item in unchecked_nodes:
            unchecked_nodes[item].in_weight = math.inf
        unchecked_nodes[source].in_weight = 0
        while len(unchecked_nodes) > 0:
            current_key = min(unchecked_nodes.items(), key=lambda node_tuple: node_tuple[1].in_weight)[1].key
            current_node = unchecked_nodes.pop(current_key)
            for key in self.g.nodes[current_key].out_going_edges:
                next_node = self.g.nodes[key]
                current_edge_weight = next_node.in_going_edges[current_key]
                if current_node.in_weight + current_edge_weight < next_node.in_weight:
                    next_node.in_weight = current_node.in_weight + current_edge_weight
                    next_node.prev_node_key = current_node.key
        for node in self.g.nodes:
            max_shortest_path = max(max_shortest_path, self.g.nodes[node].in_weight)
        return max_shortest_path

    def has_path_to_nodes(self, node_list: List[int], source):
        """
        return true if and only if there exists a path from the source to all other nodes in the list
        dfs based algorithm
        """
        self.dfs(self.g, source)
        has_path = True
        for node_key in node_list:
            has_path = has_path and self.g.nodes[node_key].visited
        return has_path

    def choose_start_nodes(self, node_lst: List[int]):
        min_dist = math.inf
        ans = ()
        for node_key in node_lst:
            if self.has_path_to_nodes(node_lst, node_key):
                self.max_shortest_path(node_key)
                for other_node_key in node_lst:
                    if node_key == other_node_key:
                        continue
                    current_in_weight = self.g.nodes[other_node_key].in_weight
                    if current_in_weight < min_dist:
                        min_dist = current_in_weight
                        ans = (node_key, other_node_key)
        return ans

    def closest_node(self, unchecked_node: List[int], source: int):
        self.max_shortest_path(source)
        result = source
        min_weight = math.inf
        for node in unchecked_node:
            if self.g.nodes[node].in_weight < min_weight:
                result = self.g.nodes[node].key
                min_weight = self.g.nodes[node].in_weight
        return result

    def transpose(self):
        transpose = copy.deepcopy(self.g)
        transpose.edges = {}
        for edge in self.g.edges:
            reversed_edge = edge[1], edge[0]
            transpose.edges[reversed_edge] = self.g.edges[edge]
        for key in transpose.nodes:
            current_node = transpose.nodes[key]
            temp = current_node.in_going_edges
            current_node.in_going_edges = current_node.out_going_edges
            current_node.out_going_edges = temp
        return transpose

    def dfs(self, graph: DiGraph, start_node: int):
        graph.reset_all_visited()
        not_visited = deque()
        not_visited.append(start_node)
        while len(not_visited) > 0:
            current_node = graph.nodes[not_visited.pop()]
            current_node.visited = True
            for neighbour in current_node.out_going_edges:
                if not graph.nodes[neighbour].visited:
                    not_visited.append(neighbour)

    def is_connected(self):
        start_node = random.choice(list(self.g.nodes.keys()))
        self.dfs(self.g, start_node)
        connected = True
        for key in self.g.nodes:
            connected = connected and self.g.nodes[key].visited
        transposed = self.transpose()
        self.dfs(transposed, start_node)
        for key in transposed.nodes:
            connected = connected and transposed.nodes[key].visited
        return connected

    def TSP(self, node_lst: List[int]) -> (List[int], float):
        """
        Finds the shortest path that visits all the nodes in the list
        :param node_lst: A list of nodes id's
        :return: A list of the nodes id's in the path, and the overall distance
        """
        if len(node_lst) == 1:  # just one node
            return node_lst, 0

        potential_starting_points = [key for key in node_lst if self.has_path_to_nodes(node_lst, key)]
        if len(potential_starting_points) == 0 or len(node_lst) == 0:  # no path exists
            return [], math.inf

        if len(node_lst) == 2:
            option_one = self.shortest_path(node_lst[0], node_lst[1])  # returns tuple: (float, list)
            option_two = self.shortest_path(node_lst[1], node_lst[0])  # returns tuple: (float, list)
            result_reversed = min(option_one, option_two, key=lambda pair: pair[0])
            # we need to return a tuple: (list, float) which is reversed from what is returned from SP func.
            return result_reversed[1], result_reversed[0]

        potential_results = []
        for source in potential_starting_points:
            node_lst_copy = node_lst[0:]
            node_lst_copy.remove(source)
            tail = self.TSP(node_lst_copy)  # (list, float)
            tail_list = tail[0]
            tail_list_lead = tail_list[0]
            head = self.shortest_path(source, tail_list_lead)  # returns (float, list)
            result_list = head[1] + tail_list[1:]  # concatenate without tail_list head because of duplicates
            result_dist = tail[1] + head[0]
            final_result = result_list, result_dist
            potential_results.append(final_result)
        return min(potential_results, key=lambda pair: pair[1])

    def centerPoint(self) -> (int, float):
        """
        Finds the node that has the shortest distance to it's farthest node.
        :return: The nodes id, min-maximum distance
        """
        if self.is_connected():
            nodes_max_dist = []
            for key in self.g.nodes:
                nodes_max_dist.append((key, self.max_shortest_path(key)))
            return min(nodes_max_dist, key=lambda pair: pair[1])
        return -1, math.inf

    def arrow_offsets(self, source, dest, r):
        source_pos = self.g.nodes[source].position
        dest_pos = self.g.nodes[dest].position
        dy = dest_pos[1] - source_pos[1]
        dx = dest_pos[0] - source_pos[0]
        distance = math.sqrt(math.pow(dx, 2) + math.pow(dy, 2))
        sin = dy / distance
        cos = dx / distance
        x_offset = r * cos
        y_offset = r * sin
        return x_offset, y_offset

    def scale(self, width, height):
        diff_x = self.g.max_x - self.g.min_x
        diff_y = self.g.max_y - self.g.min_y
        x_factor = (width - 100) / diff_x
        y_factor = (height - 100) / diff_y
        return x_factor, y_factor

    def plot_graph(self) -> None:
        """
        Plots the graph.
        If the nodes have a position, the nodes will be placed there.
        Otherwise, they will be placed in a random but elegant manner.
        @return: None
        """
        for key in self.g.nodes:
            self.g.ensure_position(key)
        root = tk.Tk()
        menubar = tk.Menu(root)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Load Graph")
        file_menu.add_command(label="Save Graph")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=root.quit())
        menubar.add_cascade(label="File", menu=file_menu)
        actions_menu = tk.Menu(menubar, tearoff=0)
        actions_menu.add_command(label="Add vertex")
        actions_menu.add_command(label="Connect Vertices")
        actions_menu.add_command(label="Remove Vertex")
        actions_menu.add_command(label="Remove Edge")
        menubar.add_cascade(label="Actions", menu=actions_menu)
        algo_menu = tk.Menu(menubar, tearoff=0)
        algo_menu.add_command(label="Shortest Path")
        algo_menu.add_command(label="Center")
        menubar.add_cascade(label="Algorithms", menu=algo_menu)
        root.config(menu=menubar)
        width = 1080
        height = 600
        root.geometry(f"{width}x{height}")
        root.title("Graph Representation")
        my_canvas = tk.Canvas(root, width=width, height=height, bg="light grey")
        my_canvas.pack()

        r = 11
        x_factor, y_factor = self.scale(width, height)
        for node in self.g.nodes:
            current_node = self.g.nodes[node]
            pos = current_node.position
            x, y, z = pos
            x = (x - self.g.min_x) * x_factor + 50
            y = (y - self.g.min_y) * y_factor + 50
            my_canvas.create_oval(x - r, y + r, x + r, y - r, fill='lawn green')
            my_canvas.create_text(x, y, text=f"{node}", fill='black', font=('ComicSans', '10', 'bold'))
        for edge in self.g.edges:
            source, dest = edge
            source_node = self.g.nodes[source]
            dest_node = self.g.nodes[dest]
            x1, y1, z1 = source_node.position
            x2, y2, z2 = dest_node.position
            x1 = (x1 - self.g.min_x) * x_factor + 50
            y1 = (y1 - self.g.min_y) * y_factor + 50
            x2 = (x2 - self.g.min_x) * x_factor + 50
            y2 = (y2 - self.g.min_y) * y_factor + 50
            x_offset, y_offset = self.arrow_offsets(source, dest, r)
            my_canvas.create_line(x1 + x_offset, y1 + y_offset, x2 - x_offset, y2 - y_offset, fill='dark slate grey',
                                  width=2,
                                  arrow=tk.LAST)
        root.resizable(True, True)

        root.mainloop()

        # raise NotImplementedError
