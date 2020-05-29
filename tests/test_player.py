import player
import pytest
import game_engine
import snake
from common import Dir


def test_generate_edges():
    p = player.BfsPlayer()
    s = game_engine.GameState()
    s.board_w = 5
    s.board_h = 5
    s.gem_x = 0
    s.gem_y = 0
    sn = snake.Snake([(2, 2)])
    sn.route = [(2, 2), (1, 2)]
    s.snake = sn

    #vertexes = p.generate_vertexes(s)
    pass


def test_gen_neighbours():

    s = {0, 1, 2, 3, 4, 5, 6, 7, 8}
    assert player.generate_neighbours(s, 0, 3) == [1, 3]
    assert player.generate_neighbours(s, 2, 3) == [5]
    assert player.generate_neighbours(s, 4, 3) == [5, 7]
    assert player.generate_neighbours(s, 8, 3) == []

    s = {0, 1, 2, 3, 5, 7, 8}
    assert player.generate_neighbours(s, 3, 3) == []


def test_gen_edges():
    s = {0, 2, 3, 5, 7, 8}
    assert player.generate_edges(s, 3) == [(0, 3), (2, 5), (5, 8), (7, 8)]


def test_bfs_player():
    p = player.BfsPlayer()

    s = game_engine.GameState()
    s.board_w = 5
    s.board_h = 5
    sn = snake.Snake([(2, 2)])
    sn.route = [(2, 2), (2, 1)]
    s.snake = sn

    p.get_direction(s)
    pass


def test_path_to_directions():
    directions = player.path_to_directions([60, 61, 62, 73], 11)
    pass


def test_get_reward():
    p = player.RlPlayer()
    s = game_engine.GameState()
    s.board_w = 11
    s.board_h = 11
    s.gem_x = 8
    s.gem_y = 5
    sn = snake.Snake([(5, 5)])
    s.snake = sn

    assert p.get_reward(s, Dir.RIGHT) == 1
    assert p.get_reward(s, Dir.UP) == -1.5
    assert p.get_reward(s, Dir.DOWN) == -1.5
    assert p.get_reward(s, Dir.LEFT) == -1.5

    s.gem_x = 2
    s.gem_y = 5
    assert p.get_reward(s, Dir.RIGHT) == -1.5
    assert p.get_reward(s, Dir.UP) == -1.5
    assert p.get_reward(s, Dir.DOWN) == -1.5
    assert p.get_reward(s, Dir.LEFT) == 1

    s.gem_x = 5
    s.gem_y = 2
    assert p.get_reward(s, Dir.RIGHT) == -1.5
    assert p.get_reward(s, Dir.UP) == 1
    assert p.get_reward(s, Dir.DOWN) == -1.5
    assert p.get_reward(s, Dir.LEFT) == -1.5

    s.gem_x = 8
    s.gem_y = 2
    assert p.get_reward(s, Dir.RIGHT) == 1
    assert p.get_reward(s, Dir.UP) == 1
    assert p.get_reward(s, Dir.DOWN) == -1.5
    assert p.get_reward(s, Dir.LEFT) == -1.5
