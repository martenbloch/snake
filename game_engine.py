class GameState:

    def __init__(self):
        self.board_w = 0
        self.board_h = 0
        self.gem_x = 0
        self.gem_y = 0
        self.snake = None

    def __str__(self):
        return "w:{} h:{} gx:{} gy:{} s:{}".format(self.board_w, self.board_h, self.gem_x, self.gem_y, self.snake)
