import pytest

import snake
import training_data as td
from common import Dir
import game_engine


def test_gen_data():
    s = snake.Snake(1, (5, 5))
    gstate = game_engine.GameState()
    gstate.board_w = 11
    gstate.board_h = 11
    gstate.gem_x = 7
    gstate.gem_y = 3
    gstate.snake = s
    data = td.game_state_to_training_data(gstate, Dir.UP)
    assert data.ml == data.mr == data.mu == data.md
    assert data.angle == 0.125

    gstate.gem_x = 3
    gstate.gem_y = 3
    data = td.game_state_to_training_data(gstate, Dir.UP)
    assert data.ml == data.mr == data.mu == data.md
    assert data.angle == 0.375

    gstate.gem_x = 3
    gstate.gem_y = 7
    data = td.game_state_to_training_data(gstate, Dir.UP)
    assert data.ml == data.mr == data.mu == data.md
    assert data.angle == 0.625

    gstate.gem_x = 7
    gstate.gem_y = 7
    data = td.game_state_to_training_data(gstate, Dir.UP)
    assert data.ml == data.mr == data.mu == data.md
    assert data.angle == 0.875

    gstate.gem_x = 5
    gstate.gem_y = 3
    data = td.game_state_to_training_data(gstate, Dir.UP)
    assert data.ml == data.mr == data.mu == data.md
    assert data.angle == 0.25

    gstate.gem_x = 5
    gstate.gem_y = 7
    data = td.game_state_to_training_data(gstate, Dir.UP)
    assert data.ml == data.mr == data.mu == data.md
    assert data.angle == 0.75

    gstate.gem_x = 3
    gstate.gem_y = 5
    data = td.game_state_to_training_data(gstate, Dir.UP)
    assert data.ml == data.mr == data.mu == data.md
    assert data.angle == 0.5


