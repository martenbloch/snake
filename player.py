import tensorflow as tf
import numpy as np
import pygame

from common import Dir
import training_data as dp


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
