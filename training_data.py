from common import Dir
import struct
import math
import numpy as np


class TrainingData:

    def __init__(self):
        self.ml = False        # can move left
        self.mr = False
        self.mu = False        # can move up
        self.md = False
        self.angle = 0
        self.direction = Dir.UP

    def to_byte_array(self):
        data = struct.pack("<4?fi", self.ml, self.mr, self.mu, self.md, self.angle, int(self.direction.value))
        return data

    def get_input_data(self):
        return [self.ml, self.mr, self.mu, self.md, self.angle]

    def get_output_data(self):
        return self.direction.value

    def __repr__(self):
        return "ml:{}  mr:{}  mu:{}  md:{}  angle:{}  direction:{}".format(self.ml, self.mr, self.mu, self.md, self.angle, self.direction)

    def __str__(self):
        return self.__repr__()


def game_state_to_training_data(a_game_state, a_direction):
    sx, sy = a_game_state.snake.get_current_pos()
    left = (sx-1, sy)
    right = (sx+1, sy)
    up = (sx, sy-1)
    down = (sx, sy+1)

    data = TrainingData()

    if sx > 0 and not a_game_state.snake.is_on_route(sx-1, sy):
        data.ml = True
    if sx < (a_game_state.board_w - 1) and not a_game_state.snake.is_on_route(sx+1, sy):
        data.mr = True
    if sy > 0 and not a_game_state.snake.is_on_route(sx, sy-1):
        data.mu = True
    if sy < (a_game_state.board_h-1) and not a_game_state.snake.is_on_route(sx, sy+1):
        data.md = True

    if a_game_state.gem_x == sx and a_game_state.gem_y < sy:
        angle = 90
    elif a_game_state.gem_x == sx and a_game_state.gem_y > sy:
        angle = 270
    elif a_game_state.gem_y == sy and a_game_state.gem_x < sx:
        angle = 180
    elif a_game_state.gem_y == sy and a_game_state.gem_x > sx:
        angle = 0
    else:
        if sx == a_game_state.gem_x and sy == a_game_state.gem_y:
            angle = 0
        else:
            angle = math.atan(abs(a_game_state.gem_y - sy)/abs(a_game_state.gem_x - sx))*180/math.pi
            if a_game_state.gem_x < sx and a_game_state.gem_y < sy:
                angle += 90
            elif a_game_state.gem_x < sx and a_game_state.gem_y > sy:
                angle += 180
            elif a_game_state.gem_x > sx and a_game_state.gem_y > sy:
                angle += 270

    data.angle = angle / 360
    data.direction = a_direction

    return data


class DataProcessor:

    def process(self, a_data):
        pass


class RemoveDuplicates(DataProcessor):

    def process(self, a_data):
        s = set()
        processed_data = []
        for i in range(len(a_data)):
            e = a_data[i]
            val = (e.ml, e.mr, e.mu, e.md, e.angle)
            if not val in s:
                s.add(val)
                processed_data.append(e)
        a_data = processed_data


class FixDirection(DataProcessor):

    def process(self, a_data):
        for i in range(len(a_data)):
            e = a_data[i]
            opt_dir = correct_direction(e.ml, e.mr, e.mu, e.md, e.angle, e.direction)
            if opt_dir != e.direction:
                print("correct direction:{}, new dir:{}".format(e, opt_dir))
            a_data[i].direction = opt_dir


def correct_direction(ml, mr, mu, md, angle, direction):
    u_angle = angle*360
    min_angle_diff = 360
    opt_dir = direction
    if ml == True and abs(u_angle-180) < min_angle_diff:
        min_angle_diff = abs(u_angle-180)
        opt_dir = Dir.LEFT
    if mr == True and abs(u_angle) < min_angle_diff:
        min_angle_diff = abs(u_angle)
        opt_dir = Dir.RIGHT
    if mu == True and abs(u_angle-90) < min_angle_diff:
        min_angle_diff = abs(u_angle-90)
        opt_dir = Dir.UP
    if md == True and abs(u_angle-270) < min_angle_diff:
        min_angle_diff = abs(u_angle-270)
        opt_dir = Dir.DOWN

    return opt_dir


def is_training_data_valid(a_data):
    if a_data.direction == Dir.UP and a_data.mu == False:
        return False
    elif a_data.direction == Dir.DOWN and a_data.md == False:
        return False
    elif a_data.direction == Dir.LEFT and a_data.ml == False:
        return False
    elif a_data.direction == Dir.RIGHT and a_data.mr == False:
        return False
    return True


def load_data(a_filename):
    training_data = []
    file = open(a_filename, "rb")
    while True:
        val = struct.Struct("<4?fi")
        data = file.read(val.size)
        if not data or len(data) != val.size:
            break
        raw_data = struct.unpack("<4?fi", data)
        d = TrainingData()
        d.ml = raw_data[0]
        d.mr = raw_data[1]
        d.mu = raw_data[2]
        d.md = raw_data[3]
        d.angle = raw_data[4]
        d.direction = Dir(raw_data[5])
        training_data.append(d)
    file.close()
    return training_data


def import_training_data(*a_files):
    data = []
    for f in a_files:
        data += load_data(f)

    data_processors = [RemoveDuplicates(), FixDirection()]

    for p in data_processors:
        p.process(data)

    # split data to in/out
    print("input size:{}".format(len(data)))
    data_size = len(data)
    train_in = np.ndarray(shape=(data_size, 1, 5))
    train_out = []

    for i in range(data_size):
        train_in[i] = data[i].get_input_data()
        train_out.append(data[i].get_output_data())

    return train_in, np.array(train_out)
