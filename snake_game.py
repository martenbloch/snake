import pygame
from random import randint
import sys

import player
import snake
import game_engine


class Renderer:

    def on_init(self):
        pass

    def render_snake(self, snake):
        pass

    def render_gem(self, gem):
        pass

    def render(self):
        pass

    def render_border(self):
        pass


class PygameRenderer(Renderer):

    def __init__(self):
        self.w = 442
        self.h = 485
        self.screen = pygame.display.set_mode((self.w, self.h))
        self.snake_gfx = SnakeGfx(self.screen)
        self.gem_gfx = GemGfx(self.screen)
        self.points = 0

    def on_init(self):
        print("pygame on_init")

    def render_snake(self, a_snake):
        self.snake_gfx.route = a_snake
        self.snake_gfx.draw()
        self.points = a_snake.length - 1

    def render_gem(self, gem):
        self.screen.fill((0, 0, 0))
        self.gem_gfx.gem = gem
        self.gem_gfx.draw()

    def render(self):
        pass
        pygame.display.flip()

    def render_border(self):
        r = pygame.Rect(0, 0, 440, 440)
        pygame.draw.rect(self.screen, (17, 250, 7), r, 2)

        font = pygame.font.Font('freesansbold.ttf', 32)
        text = font.render("Score:{}".format(self.points), True, (17, 250, 7), (0, 0, 0))
        textRect = text.get_rect()
        textRect.top = 450
        self.screen.blit(text, textRect)

        pygame.display.update()


class Board:

    def __init__(self, w, h):
        self.w = w
        self.h = h

    def is_on_board(self, x, y):
        if x >= 0 and x < self.w and y >= 0 and y < self.h:
            return True
        return False


class Gem:

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def get_pos(self):
        return self.x, self.y

    def set_pos(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return "x:{}  y:{}".format(self.x, self.y)


class SnakeGame:
    def __init__(self, a_player, a_renderer, a_speed, a_show_gui):
        self.player = a_player
        self.renderer = a_renderer
        self.board = Board(11, 11)
        self.snake_route = snake.Snake([(5, 5)])
        self.gem = Gem(*self.generate_gem_new_pos())
        self.speed = a_speed
        self.show_gui = a_show_gui

    def set_direction(self, a_direction):
        self.snake_route.set_dir(a_direction)

    def step(self):
        if not self.snake_route.update_position():
            return False

        x, y = self.snake_route.get_current_pos()
        if self.board.is_on_board(x, y) == False:
            return False

        if self.snake_route.is_on_route(*self.gem.get_pos()):
            self.snake_route.increase()
            self.gem.set_pos(*self.generate_gem_new_pos())

    def get_state(self):
        pass

    def run(self):
        timer_event = pygame.USEREVENT + 1
        pygame.time.set_timer(timer_event, self.speed)

        while True:
            # create game state object
            # TODO: move to helper function
            #gstate = game_engine.GameState()
            #gstate.board_w = self.board.w
            #gstate.board_h = self.board.h
            #gstate.gem_x = self.gem.x
            #gstate.gem_y = self.gem.y
            #gstate.snake = self.snake_route
            gstate = self.get_game_state()

            if self.speed > 0:
                for event in pygame.event.get(timer_event):
                    if event.type == timer_event:
                        direction = self.player.get_direction(gstate)
                        self.set_direction(direction)
                        if self.step() == False:
                            print("Game over, points: {}".format(self.snake_route.length-1))
                            self.player.game_over()
                            return
            else:
                direction = self.player.get_direction(gstate)
                self.set_direction(direction)
                if self.step() == False:
                    print("Game over, points: {}".format(self.snake_route.length - 1))
                    self.player.game_over()
                    return

            if self.show_gui:
                self.renderer.render_gem(self.gem)
                self.renderer.render_snake(self.snake_route)
                self.renderer.render_border()
                self.renderer.render()

    def generate_gem_new_pos(self):
        while True:
            x = randint(0, self.board.w-1)
            y = randint(0, self.board.h-1)
            if not self.snake_route.is_on_route(x, y):
                return x, y

    def get_gem(self):
        return self.gem

    def get_snake(self):
        return self.snake_route

    def get_points(self):
        return self.snake_route.length-1

    def get_game_state(self):
        gstate = game_engine.GameState()
        gstate.board_w = self.board.w
        gstate.board_h = self.board.h
        gstate.gem_x = self.gem.x
        gstate.gem_y = self.gem.y
        gstate.snake = self.snake_route
        return gstate


class SnakeGfx:

    def __init__(self, screen):
        self.screen = screen
        self.image = pygame.image.load("gfx/snake-block.png")

    def draw(self):
        for point in self.route.get_route():
            x, y = point
            self.screen.blit(self.image, (x*40, y*40))


class GemGfx:

    def __init__(self, screen):
        self.screen = screen
        self.image = pygame.image.load("gfx/gem-block.png")

    def draw(self):
        x, y = self.gem.get_pos()
        self.screen.blit(self.image, (x*40, y*40))


if __name__ == "__main__":

    player_type = sys.argv[1]
    p = None
    if player_type == "ai":
        ai_model = sys.argv[2]
        p = player.AiPlayer(ai_model)
    elif player_type == "human":
        if len(sys.argv) == 3:
            dump_file = sys.argv[2]
            p = player.HumanPlayerSaveState(player.HumanPlayer(), dump_file)
        else:
            p = player.HumanPlayer()
    elif player_type == "bfs":
        p = player.BfsPlayer()
    else:
        print("Incorrect player type: {}".format(player_type))
        exit()

    pygame.init()
    renderer = PygameRenderer()

    game = SnakeGame(p, renderer, 150, True)
    game.run()

    if player_type == "human" and sys.argv[2]:
        p.save_data()
