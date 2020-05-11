import tensorflow as tf
import numpy as np
import pygame
import random
from tensorflow import keras

from common import Dir
import training_data as dp
import algorithms.graph_algorithms
import copy

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
        self.prev_pts = None
        self.gamma = 0.9
        self.epsilon = 1

        self.model = keras.Sequential([
            keras.layers.Flatten(input_shape=(1, 5)),
            keras.layers.Dense(174, activation=tf.nn.relu6),
            keras.layers.Dense(4, activation=tf.nn.softmax)
        ])

        self.model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
        self.experience = []

    def get_direction(self, a_game_state):
        print("get direction")
        if random.randint(0, 1) < self.epsilon:
            direction = Dir(random.randint(0, 3))
        else:
            s = dp.game_state_to_training_data(a_game_state, Dir.UP)
            input_data = np.ndarray(shape=(1, 1, 5))
            input_data[0] = s.get_input_data()
            direction = Dir(np.argmax(self.model.predict(input_data)))
            print("NN predict")

        if self.prev_state:
            is_game_over = False
            reward = 0
            if (a_game_state.snake.length-1) != self.prev_pts:
                reward = 10
            #self.experience.append([copy.deepcopy(self.prev_state), direction, reward, copy.deepcopy(a_game_state), is_game_over])
            self.experience.append(self.create_training_data(copy.deepcopy(self.prev_state), direction, reward, copy.deepcopy(a_game_state), is_game_over))

        self.train_on_batch()

        self.prev_state = copy.deepcopy(a_game_state)
        self.prev_dir = direction
        self.prev_pts = a_game_state.snake.length - 1

        return direction

    def game_over(self):
        reward = -10
        self.experience.append(self.create_training_data(copy.deepcopy(self.prev_state), self.prev_dir, reward, copy.deepcopy(self.prev_state), True))

        self.prev_state = None
        self.prev_dir = None
        self.prev_pts = None

    def set_epsilon(self, a_val):
        self.epsilon = a_val

    def train_on_batch(self):

        batch_size = 10

        if len(self.experience) == 0:
            return

        size = min(batch_size, len(self.experience))
        train_in = np.ndarray(shape=(size, 1, 5))
        train_out = []
        exp = random.sample(self.experience, size)

        for i in range(len(exp)):
            t_in, t_out = exp[i]
            train_in[i] = t_in
            train_out.append(t_out)
        self.model.fit(train_in, np.array(train_out), epochs=1)
        """
        

        size = min(batch_size, len(self.experience))
        train_inx = np.ndarray(shape=(size, 1, 5))


        exp = random.sample(self.experience, size)
        print("train on batch :{}".format(len(exp)))
        for e in exp:
            reward = e[2]

            train_in = dp.game_state_to_training_data(e[0], Dir.UP)
            input_data = np.ndarray(shape=(1, 1, 5))
            input_data[0] = train_in.get_input_data()
            train_inx[0] = input_data

            s = dp.game_state_to_training_data(e[3], Dir.UP)
            si = np.ndarray(shape=(1, 1, 5))
            si[0] = s.get_input_data()
            qn = reward + self.gamma * self.model.predict(si).max()

            #self.model.predict(si)
            out = self.model.predict(input_data)
            out[0][e[1].value] = qn

            outputs.append(np.argmax(out))
        self.model.fit(train_inx, np.array(outputs), epochs=1)
        """

    def create_training_data(self, a_state, a_direction, a_reward, a_next_state, a_is_game_over):
        train_in = []
        train_out = 0

        t_in = dp.game_state_to_training_data(a_state, Dir.UP)
        train_in = t_in.get_input_data()

        if a_is_game_over == False:
            s = dp.game_state_to_training_data(a_next_state, Dir.UP)
            si = np.ndarray(shape=(1, 1, 5))
            si[0] = s.get_input_data()
            qn = a_reward + self.gamma * self.model.predict(si).max()
        else:
            qn = a_reward

        # self.model.predict(si)
        input_data = np.ndarray(shape=(1, 1, 5))
        input_data[0] = t_in.get_input_data()
        out = self.model.predict(input_data)
        out[0][a_direction.value] = qn

        train_out = np.argmax(out)

        return train_in, train_out
