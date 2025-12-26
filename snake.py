import pygame
import sys
import random
from pygame.math import Vector2

# --- CONFIGURATION ---
CELL_SIZE = 30
CELL_NUMBER = 20
UI_HEIGHT = 60
SCREEN_WIDTH = CELL_SIZE * CELL_NUMBER
SCREEN_HEIGHT = (CELL_SIZE * CELL_NUMBER) + UI_HEIGHT
FPS = 60
GAME_SPEED = 150

# --- POLISHED "FLAT DESIGN" PALETTE ---
COLORS = {
    'bg_main': (46, 52, 64),  # Dark Grey-Blue
    'bg_grid_1': (55, 60, 75),  # Slightly lighter checker
    'bg_grid_2': (46, 52, 64),  # Base background
    'ui_bar': (35, 39, 48),  # Darker top bar
    'snake_body': (136, 192, 208),  # Soft Cyan/Blue
    'snake_head': (129, 161, 193),  # Slightly darker Blue
    'snake_border': (76, 86, 106),  # Dark Blue-Grey outline
    'apple': (191, 97, 106),  # Soft Red
    'leaf': (163, 190, 140),  # Soft Green
    'text': (236, 239, 244),  # White-ish
    'text_sub': (216, 222, 233),  # Grey-ish
    'win_border': (235, 203, 139)  # Gold/Yellow
}


class Snake:
    def __init__(self):
        self.reset()

    def reset(self):
        self.body = [Vector2(5, 10), Vector2(4, 10), Vector2(3, 10)]
        self.direction = Vector2(1, 0)
        self.new_block = False
        # FIX: Input lock flag
        self.can_move = True

    def draw_snake(self, screen):
        for index, block in enumerate(self.body):
            x_pos = int(block.x * CELL_SIZE)
            y_pos = int(block.y * CELL_SIZE) + UI_HEIGHT
            block_rect = pygame.Rect(x_pos, y_pos, CELL_SIZE, CELL_SIZE)

            color = COLORS['snake_head'] if index == 0 else COLORS['snake_body']
            pygame.draw.rect(screen, color, block_rect, border_radius=6)
            pygame.draw.rect(screen, COLORS['snake_border'], block_rect, 1, border_radius=6)

            if index == 0:
                self.draw_eyes(screen, block_rect)

    def draw_eyes(self, screen, head_rect):
        center_x, center_y = head_rect.center
        eye_radius = 4
        pupil_radius = 2
        offset = 6

        if self.direction == Vector2(1, 0):  # Right
            eye_1 = (center_x + offset, center_y - offset)
            eye_2 = (center_x + offset, center_y + offset)
        elif self.direction == Vector2(-1, 0):  # Left
            eye_1 = (center_x - offset, center_y - offset)
            eye_2 = (center_x - offset, center_y + offset)
        elif self.direction == Vector2(0, -1):  # Up
            eye_1 = (center_x - offset, center_y - offset)
            eye_2 = (center_x + offset, center_y - offset)
        else:  # Down
            eye_1 = (center_x - offset, center_y + offset)
            eye_2 = (center_x + offset, center_y + offset)

        pygame.draw.circle(screen, (255, 255, 255), eye_1, eye_radius)
        pygame.draw.circle(screen, (255, 255, 255), eye_2, eye_radius)
        pygame.draw.circle(screen, (0, 0, 0), eye_1, pupil_radius)
        pygame.draw.circle(screen, (0, 0, 0), eye_2, pupil_radius)

    def move_snake(self):
        if self.new_block:
            body_copy = self.body[:]
            body_copy.insert(0, body_copy[0] + self.direction)
            self.body = body_copy
            self.new_block = False
        else:
            body_copy = self.body[:-1]
            body_copy.insert(0, body_copy[0] + self.direction)
            self.body = body_copy

        # FIX: Unlock input after move is processed
        self.can_move = True

    def add_block(self):
        self.new_block = True


class Fruit:
    def __init__(self):
        self.randomize()

    def randomize(self):
        self.x = random.randint(0, CELL_NUMBER - 1)
        self.y = random.randint(0, CELL_NUMBER - 1)
        self.pos = Vector2(self.x, self.y)

    def draw_fruit(self, screen):
        x_pos = int(self.pos.x * CELL_SIZE)
        y_pos = int(self.pos.y * CELL_SIZE) + UI_HEIGHT
        center_x = x_pos + CELL_SIZE // 2
        center_y = y_pos + CELL_SIZE // 2

        pygame.draw.circle(screen, COLORS['apple'], (center_x, center_y + 2), CELL_SIZE // 2 - 4)
        pygame.draw.circle(screen, (255, 200, 200), (center_x - 4, center_y - 4), 3)
        pygame.draw.line(screen, (60, 40, 40), (center_x, center_y - 8), (center_x, center_y - 14), 3)
        pygame.draw.ellipse(screen, COLORS['leaf'], pygame.Rect(center_x, center_y - 16, 8, 6))


class Main:
    def __init__(self):
        self.snake = Snake()
        self.fruit = Fruit()
        self.score = 0
        self.state = "START"

    def update(self):
        if self.state == "PLAYING":
            self.snake.move_snake()
            self.check_collision()
            self.check_fail()

    def draw_elements(self, screen):
        self.draw_grid(screen)

        if self.state == "START":
            self.draw_ui_header(screen)
            self.draw_message(screen, "SNAKE", "Press Arrows to Start")

        elif self.state == "PLAYING":
            self.fruit.draw_fruit(screen)
            self.snake.draw_snake(screen)
            self.draw_ui_header(screen)

        elif self.state == "GAMEOVER":
            self.draw_grid(screen)
            self.fruit.draw_fruit(screen)
            self.snake.draw_snake(screen)
            self.draw_ui_header(screen)
            self.draw_message(screen, "GAME OVER", "Press 'R' to Restart")

        elif self.state == "WIN":
            self.draw_grid(screen)
            self.snake.draw_snake(screen)
            self.draw_ui_header(screen)
            self.draw_message(screen, "YOU WON!", "Perfect Game! Press 'R'", is_win=True)

    def draw_grid(self, screen):
        screen.fill(COLORS['bg_main'])
        for row in range(CELL_NUMBER):
            for col in range(CELL_NUMBER):
                if (row + col) % 2 == 0:
                    color = COLORS['bg_grid_1']
                else:
                    color = COLORS['bg_grid_2']
                rect = pygame.Rect(col * CELL_SIZE, row * CELL_SIZE + UI_HEIGHT, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(screen, color, rect)

    def draw_ui_header(self, screen):
        header_rect = pygame.Rect(0, 0, SCREEN_WIDTH, UI_HEIGHT)
        pygame.draw.rect(screen, COLORS['ui_bar'], header_rect)
        pygame.draw.line(screen, (25, 30, 35), (0, UI_HEIGHT), (SCREEN_WIDTH, UI_HEIGHT), 2)

        score_text = f"SCORE: {self.score}"
        text_surf = game_font.render(score_text, True, COLORS['text'])
        text_rect = text_surf.get_rect(midleft=(20, UI_HEIGHT // 2))
        screen.blit(text_surf, text_rect)

        title_surf = game_font.render("Q: Quit", True, COLORS['text_sub'])
        title_rect = title_surf.get_rect(midright=(SCREEN_WIDTH - 20, UI_HEIGHT // 2))
        screen.blit(title_surf, title_rect)

    def draw_message(self, screen, title, subtitle, is_win=False):
        overlay_width = 320
        overlay_height = 160
        overlay_rect = pygame.Rect(
            (SCREEN_WIDTH - overlay_width) // 2,
            (SCREEN_HEIGHT - overlay_height) // 2,
            overlay_width,
            overlay_height
        )

        shadow_rect = overlay_rect.copy()
        shadow_rect.move_ip(4, 4)
        pygame.draw.rect(screen, (20, 20, 20), shadow_rect, border_radius=15)

        pygame.draw.rect(screen, COLORS['ui_bar'], overlay_rect, border_radius=15)

        border_col = COLORS['win_border'] if is_win else COLORS['text_sub']
        pygame.draw.rect(screen, border_col, overlay_rect, 2, border_radius=15)

        title_col = COLORS['win_border'] if is_win else COLORS['text']

        title_surf = title_font.render(title, True, title_col)
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, overlay_rect.centery - 20))

        sub_surf = game_font.render(subtitle, True, COLORS['text_sub'])
        sub_rect = sub_surf.get_rect(center=(SCREEN_WIDTH // 2, overlay_rect.centery + 30))

        screen.blit(title_surf, title_rect)
        screen.blit(sub_surf, sub_rect)

    def check_collision(self):
        if self.fruit.pos == self.snake.body[0]:
            self.snake.add_block()
            self.score += 1

            if len(self.snake.body) == CELL_NUMBER * CELL_NUMBER:
                self.game_won()
                return

            self.fruit.randomize()
            while self.fruit.pos in self.snake.body:
                self.fruit.randomize()

    def check_fail(self):
        if not 0 <= self.snake.body[0].x < CELL_NUMBER or not 0 <= self.snake.body[0].y < CELL_NUMBER:
            self.game_over()
        for block in self.snake.body[1:]:
            if block == self.snake.body[0]:
                self.game_over()

    def game_over(self):
        self.state = "GAMEOVER"

    def game_won(self):
        self.state = "WIN"

    def reset_game(self):
        self.snake.reset()
        self.score = 0
        self.state = "PLAYING"
        self.fruit.randomize()


# --- SETUP ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Snake Clean Edition')
clock = pygame.time.Clock()

try:
    game_font = pygame.font.SysFont('calibri', 24, bold=True)
    title_font = pygame.font.SysFont('calibri', 50, bold=True)
except:
    game_font = pygame.font.Font(None, 30)
    title_font = pygame.font.Font(None, 60)

SCREEN_UPDATE = pygame.USEREVENT
pygame.time.set_timer(SCREEN_UPDATE, GAME_SPEED)

main_game = Main()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == SCREEN_UPDATE and main_game.state == "PLAYING":
            main_game.update()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                pygame.quit()
                sys.exit()

            if main_game.state == "START":
                if event.key in [pygame.K_UP, pygame.K_DOWN, pygame.K_RIGHT, pygame.K_LEFT]:
                    main_game.state = "PLAYING"

            elif main_game.state == "GAMEOVER" or main_game.state == "WIN":
                if event.key == pygame.K_r:
                    main_game.reset_game()

            # --- INPUT HANDLING WITH LOCK FIX ---
            if main_game.state == "PLAYING":
                # Only check keys if we haven't moved yet this frame
                if main_game.snake.can_move:
                    if event.key == pygame.K_UP and main_game.snake.direction.y != 1:
                        main_game.snake.direction = Vector2(0, -1)
                        main_game.snake.can_move = False  # Lock input
                    if event.key == pygame.K_RIGHT and main_game.snake.direction.x != -1:
                        main_game.snake.direction = Vector2(1, 0)
                        main_game.snake.can_move = False  # Lock input
                    if event.key == pygame.K_DOWN and main_game.snake.direction.y != -1:
                        main_game.snake.direction = Vector2(0, 1)
                        main_game.snake.can_move = False  # Lock input
                    if event.key == pygame.K_LEFT and main_game.snake.direction.x != 1:
                        main_game.snake.direction = Vector2(-1, 0)
                        main_game.snake.can_move = False  # Lock input

    main_game.draw_elements(screen)
    pygame.display.update()
    clock.tick(FPS)