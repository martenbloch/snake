import training_data
import snake_game
import player
from common import Dir
import random
import pygame

import numpy as np


def train(a_num_games):
    q_table = {}
    p = player.Player()
    r = snake_game.Renderer()
    learning_rate = 0.0005
    gamma = 0.7

    for i in range(a_num_games):
        game = snake_game.SnakeGame(p, r)
        while True:
            #print("step")
            s1 = game.get_game_state()
            s = training_data.game_state_to_training_data(s1, Dir.UP)
            state = (s.mu, s.md, s.ml, s.mr, s.angle)
            direction = None
            reward = -0.1
            points = game.get_points()
            if state in q_table:
                action = np.argmax(q_table[state])
                if action == 0:
                    direction = Dir.UP
                if action == 1:
                    direction = Dir.DOWN
                if action == 2:
                    direction = Dir.LEFT
                if action == 3:
                    direction = Dir.RIGHT
            else:
                q_table[state] = [0, 0, 0, 0]
                direction = Dir.UP

            val = random.randint(0,3)
            if val == 0:
                direction = Dir.UP
            if val == 1:
                direction = Dir.DOWN
            if val == 2:
                direction = Dir.LEFT
            if val == 3:
                direction = Dir.RIGHT

            #print(direction)
            idx = direction.value
            game.set_direction(direction)
            if game.step() == False:
                reward = -10
                # update q value
                nq = reward
                q_table[state][idx] = nq
                #print("Game over, pts:{}".format(game.get_points()))
                break
            else:
                #print(s1)
                if game.get_points() > points:
                    reward = 10
                # update q value
                ns = game.get_game_state()
                ns = training_data.game_state_to_training_data(ns, Dir.UP)
                ns = (s.mu, s.md, s.ml, s.mr, s.angle)

                nr = 0
                if ns in q_table:
                    nr = max(q_table[ns])
                else:
                    q_table[ns] = [0, 0, 0, 0]

                nq = reward + gamma * nr
                q_table[state][idx] = nq

    # test game
    game = snake_game.SnakeGame(p, r)
    while True:
        s1 = game.get_game_state()
        s = training_data.game_state_to_training_data(s1, Dir.UP)
        state = (s.mu, s.md, s.ml, s.mr, s.angle)
        direction = None
        if state in q_table:
            action = np.argmax(q_table[state])
            if action == 0:
                direction = Dir.UP
            if action == 1:
                direction = Dir.DOWN
            if action == 2:
                direction = Dir.LEFT
            if action == 3:
                direction = Dir.RIGHT
        else:
            direction = Dir.UP
            print("default UP")

        game.set_direction(direction)
        if game.step() == False:
            print("Game over, pts:{}".format(game.get_points()))
            break


if __name__ == "__main__":
    print("Reinforcement learning")
    #train(50)

    pygame.init()
    renderer = snake_game.PygameRenderer()
    p = player.RlPlayer()

    epsilon_decay_linear = 1/75
    epsilon = 1
    n_runs = 50
    for i in range(n_runs):
        print("episode:{}, epsilon:{}".format(i, epsilon))
        game = snake_game.SnakeGame(p, renderer, 200)
        game.run()
        epsilon = 1 - (i/n_runs)
        p.set_epsilon(epsilon)
        if i%100 == 0:
            pass
    pass
