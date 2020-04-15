from common import Dir


class Snake:

    def __init__(self, length, pos):
        self.length = length
        self.route = [pos]
        self.dir = Dir.DOWN

    def increase(self):
        self.length = self.length + 1

    def update_position(self):
        x, y = self.route[-1]

        if self.dir.value == Dir.UP.value:
            y = y - 1
        elif self.dir.value == Dir.DOWN.value:
            y = y + 1
        elif self.dir.value == Dir.LEFT.value:
            x = x - 1
        elif self.dir.value == Dir.RIGHT.value:
            x = x + 1

        if self.is_on_route(x, y):
            print("Game over - body collision x:" + str(x) + " y: " + str(y))
            return False

        self.route.append((x, y))

        if len(self.route) > self.length:
            self.route.pop(0)

        return True

    def set_dir(self, direction):
        self.dir = direction

    def get_current_pos(self):
        return self.route[-1]

    def get_route(self):
        return self.route

    def is_on_route(self, x, y):
        for point in self.route:
            px, py = point
            if px == x and py == y:
                return True
        return False

    def __repr__(self):
        return "snake:{}".format(self.route)
