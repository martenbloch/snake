import tensorflow as tf
import numpy as np
import pygame
import random
from tensorflow import keras

from common import Dir
import training_data as dp
import algorithms.graph_algorithms
import copy
import math


class Player:

    def get_direction(self, a_game_state):
        pass

    def game_over(self):
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


class RlPlayer(Player):

    def __init__(self):
        self.q_table = {}
        self.prev_state = None
        self.prev_dir = None
        self.epsilon = 1
        self.learning_rate = 1
        self.gamma = 0

        self.model = keras.Sequential([
            keras.layers.Flatten(input_shape=(1, 5)),
            keras.layers.Dense(174, activation=tf.nn.relu6),
            keras.layers.Dense(4, activation=tf.nn.softmax)
        ])

        self.model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

    def get_direction(self, a_game_state):
        r = random.randint(0, 1)
        if r < self.epsilon:
            direction = Dir(random.randint(0, 3))
        else:
            key = dp.game_state_to_training_data(a_game_state, Dir.UP).get_input_data()
            direction = Dir(np.argmax(self.q_table.setdefault(key, [0, 0, 0, 0])))

        if self.prev_state:
            reward = self.get_reward(self.prev_state, self.prev_dir, False)

            key = dp.game_state_to_training_data(self.prev_state, self.prev_dir).get_input_data()
            value = self.q_table.setdefault(key, [0, 0, 0, 0])

            # update q value
            max_future_reward = 0

            new_key = tuple(dp.game_state_to_training_data(a_game_state, direction).get_input_data())
            if new_key in self.q_table:
                max_future_reward = max(self.q_table[new_key])

            value[self.prev_dir.value] = (1 - self.learning_rate) * value[self.prev_dir.value] + self.learning_rate * (reward + self.gamma * max_future_reward)

        self.prev_state = copy.deepcopy(a_game_state)
        self.prev_dir = direction

        return direction

    def game_over(self):
        key = dp.game_state_to_training_data(self.prev_state, self.prev_dir).get_input_data()
        value = self.q_table.setdefault(key, [0, 0, 0, 0])

        value[self.prev_dir.value] = (1 - self.learning_rate) * value[self.prev_dir.value] + self.learning_rate * self.get_reward(self.prev_state, self.prev_dir, True)

        self.prev_state = None
        self.prev_dir = None

    def set_epsilon(self, a_val):
        self.epsilon = a_val

    def replay_memory(self, a_model_name):

        if len(self.q_table) == 0:
            return

        # remove items that were not fully explored
        self.q_table = {k: v for k, v in self.q_table.items() if v[0] != 0 and v[1] != 0 and v[2] != 0 and v[3] != 0}

        train_in = np.ndarray(shape=(len(self.q_table), 1, 5))
        train_out = []

        i = 0
        for k, v in self.q_table.items():
            train_in[i] = k
            train_out.append(np.argmax(v))
            i += 1

        self.model.fit(train_in, np.array(train_out), epochs=200)

        tf.keras.models.save_model(self.model, a_model_name, overwrite=True, include_optimizer=True)

    def get_reward(self, a_state, a_direction, a_is_game_over):

        if a_is_game_over:
            return -10

        t_in = dp.game_state_to_training_data(a_state, a_direction)
        opt_dir = dp.correct_direction(t_in.ml, t_in.mr, t_in.mu, t_in.md, t_in.angle, a_direction)

        x1, y1 = a_state.snake.get_current_pos()
        x2 = a_state.gem_x
        y2 = a_state.gem_y

        if a_direction == Dir.UP:
            y1 = y1 - 1
        elif a_direction == Dir.RIGHT:
            x1 = x1 + 1
        elif a_direction == Dir.LEFT:
            x1 = x1 - 1
        elif a_direction == Dir.DOWN:
            y1 = y1 + 1

        if x1 == x2 and y1 == y2:
            return 10

        if opt_dir.value == a_direction.value:
            return 1
        else:
            return -5
