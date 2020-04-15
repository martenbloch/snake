import training_data as td
from common import Dir


def test_best_direction():

    assert td.correct_direction(True, True, True, True, 75/360, Dir.DOWN) == Dir.UP
    assert td.correct_direction(True, True, True, True, 5 / 360, Dir.DOWN) == Dir.RIGHT
    assert td.correct_direction(True, True, True, True, 175 / 360, Dir.DOWN) == Dir.LEFT
    assert td.correct_direction(True, True, True, True, 260 / 360, Dir.LEFT) == Dir.DOWN
    assert td.correct_direction(False, False, False, True, 0 / 360, Dir.RIGHT) == Dir.DOWN
    assert td.correct_direction(False, False, False, True, 360 / 360, Dir.RIGHT) == Dir.DOWN
    assert td.correct_direction(False, False, False, True, 45 / 360, Dir.RIGHT) == Dir.DOWN