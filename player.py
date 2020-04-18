import tensorflow as tf
import numpy as np
import pygame

from common import Dir
import training_data as dp
import algorithms.graph_algorithms


class Player:

    def get_direction(self, a_game_state):
        pass


class HumanPlayer(Player):

    def __init__(self):
        self.dir = Dir.UP

    def get_direction(self, a_game_state):
        for event in pygame.event.get(pygame.KEYDOWN):
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.dir = Dir.UP
                    return Dir.UP
                elif event.key == pygame.K_DOWN:
                    self.dir = Dir.DOWN
                    return Dir.DOWN
                elif event.key == pygame.K_LEFT:
                    self.dir = Dir.LEFT
                    return Dir.LEFT
                elif event.key == pygame.K_RIGHT:
                    self.dir = Dir.RIGHT
                    return Dir.RIGHT
        return self.dir

    def save_state(self):
        pass


class HumanPlayerSaveState(Player):

    def __init__(self, a_human_player, a_dump_file):
        self.player = a_human_player
        self.training_data = []
        self.dump_file = a_dump_file

    def get_direction(self, a_game_state):
        # save state to file
        direction = self.player.get_direction(a_game_state)

        ai_input = dp.game_state_to_training_data(a_game_state, direction)

        if not dp.is_training_data_valid(ai_input):
            print("Invalid data. state:{} , ai_input:{}".format(a_game_state, ai_input))
        self.training_data.append(ai_input)
        return direction

    def save_data(self):
        data = bytearray()
        for e in self.training_data[:-1]:
            data.extend(e.to_byte_array())
        print("dump file")
        file = open(self.dump_file, "wb")
        file.write(data)
        file.close()


class AiPlayer(Player):

    def __init__(self, a_file_path):
        self.model = tf.keras.models.load_model(a_file_path)

    def get_direction(self, a_game_state):
        d = dp.game_state_to_training_data(a_game_state, Dir.UP)

        input_data = np.ndarray(shape=(1, 1, 5))
        input_data[0] = [d.ml, d.mr, d.mu, d.md, d.angle]

        direction = np.argmax(self.model.predict(input_data))
        if direction == 0:
            return Dir.UP
        elif direction == 1:
            return Dir.DOWN
        elif direction == 2:
            return Dir.LEFT
        elif direction == 3:
            return Dir.RIGHT
        else:
            print("Exception raised should be")
            return Dir.UP


class BfsPlayer(Player):

    def __init__(self):
        self.directions = []

    def get_direction(self, a_game_state):

        if len(self.directions) == 0:

            w = a_game_state.board_w
            h = a_game_state.board_h

            s1 = {s for s in range(w*h)}
            s2 = {point_to_vertex(e[0], e[1], w) for e in a_game_state.snake.get_route()[:-1]}

            vertexes = s1 - s2
            edges = generate_edges(vertexes, w)

            g = algorithms.graph_algorithms.UnweightedGraph(edges)
            snake_head = a_game_state.snake.get_route()[-1]
            snake_vertex = point_to_vertex(snake_head[0], snake_head[1], w)

            gem_vertex = point_to_vertex(a_game_state.gem_x, a_game_state.gem_y, w)

            result = algorithms.graph_algorithms.breadth_first_search(g, snake_vertex)
            path = algorithms.graph_algorithms.get_path(result, gem_vertex)

            self.directions = path_to_directions(path, w)
            self.directions.reverse()
            if len(self.directions) == 0:
                print("BfsPlayer - path not found")
                return Dir.UP

        return self.directions.pop()


def point_to_vertex(x, y, w):
        return x + y * w


def generate_edges(vertex_set, w):
        edges = []
        for v in vertex_set:
            n = generate_neighbours(vertex_set, v, w)
            for e in n:
                edges.append((v, e))
        return edges


def generate_neighbours(vertex_set, vertex, w):
        neigh = []
        vertex_row = vertex // w

        v1 = vertex + 1
        v2 = (vertex_row+1)*w + vertex % w

        if vertex_row == v1 // w and v1 in vertex_set:
            neigh.append(v1)

        if v2 in vertex_set:
            neigh.append(v2)

        return neigh


def path_to_directions(path, w):
    directions = []
    size = len(path)
    for i in range(size):
        if i+1 < size:
            ri = path[i] // w
            rn = path[i+1] // w

            if ri == rn and path[i] > path[i+1]:
                directions.append(Dir.LEFT)
            elif ri == rn and path[i] < path[i+1]:
                directions.append(Dir.RIGHT)
            elif ri > rn:
                directions.append(Dir.UP)
            else:
                directions.append(Dir.DOWN)

    return directions
