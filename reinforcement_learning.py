import snake_game
import player
import pygame


if __name__ == "__main__":
    print("Reinforcement learning")

    pygame.init()
    renderer = snake_game.PygameRenderer()
    p = player.RlPlayer()

    epsilon_decay_linear = 1/75
    epsilon = 1
    n_runs = 5000
    pts = []

    for i in range(n_runs):
        print("episode:{}, epsilon:{}".format(i, epsilon))
        game = snake_game.SnakeGame(p, renderer, 0, False)
        game.run()
        epsilon = 1 - (i/n_runs)
        p.set_epsilon(epsilon)
        pts.append(game.get_points())
    print("----------FIANL RUN --------------")

    epsilon = 0
    for i in range(500):
        print("episode:{}, epsilon:{}".format(i, epsilon))
        game = snake_game.SnakeGame(p, renderer, 0, False)
        game.run()
        p.set_epsilon(epsilon)
        pts.append(game.get_points())
    print("----------REPLAY MEMORY --------------")

    p.replay_memory("model-rlx")
    print(pts)
    print("max score:{}".format(max(pts)))
    print("Q-table: {}".format(len(p.q_table)))
