"""Игра «Изгиб Питона»."""

import random
from typing import List, Optional, Set, Tuple

import pygame

GRID_SIZE = 20
GRID_WIDTH = 32
GRID_HEIGHT = 24

SCREEN_WIDTH = GRID_WIDTH * GRID_SIZE
SCREEN_HEIGHT = GRID_HEIGHT * GRID_SIZE

BOARD_BACKGROUND_COLOR = (0, 0, 0)

APPLE_COLOR = (255, 0, 0)
SNAKE_COLOR = (0, 255, 0)

UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

START_DIRECTION = RIGHT
GAME_SPEED = 20

CENTER_POSITION = (
    SCREEN_WIDTH // 2,
    SCREEN_HEIGHT // 2,
)


class GameObject:
    """Базовый класс игровых объектов."""

    def __init__(
        self,
        position: Tuple[int, int] = CENTER_POSITION,
    ) -> None:
        """Инициализировать объект."""
        self.position = position
        self.body_color = None

    def draw(self, surface: pygame.Surface) -> None:
        """Отрисовать объект."""
        pass

    def draw_cell(
        self,
        surface: pygame.Surface,
        position: Tuple[int, int]
    ) -> None:
        """Нарисовать одну ячейку на игровом поле."""
        rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(surface, self.body_color, rect)


class Apple(GameObject):
    """Класс яблока."""

    def __init__(
        self,
        occupied_cells: Optional[Set[Tuple[int, int]]] = None,
    ) -> None:
        """Создать яблоко."""
        super().__init__()
        self.body_color = APPLE_COLOR
        self.randomize_position(occupied_cells)

    def randomize_position(
        self,
        occupied_cells: Optional[Set[Tuple[int, int]]] = None,
    ) -> None:
        """Сгенерировать новую позицию яблока."""
        if occupied_cells is None:
            occupied_cells = set()

        if len(occupied_cells) >= GRID_WIDTH * GRID_HEIGHT:
            return

        while True:
            new_position = (
                random.randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                random.randint(0, GRID_HEIGHT - 1) * GRID_SIZE,
            )

            if new_position not in occupied_cells:
                self.position = new_position
                break

    def draw(self, surface: pygame.Surface) -> None:
        """Отрисовать яблоко."""
        self.draw_cell(surface, self.position)


class Snake(GameObject):
    """Класс змейки."""

    def __init__(self) -> None:
        """Создать змейку."""
        super().__init__()

        self.length = 1
        self.positions: List[Tuple[int, int]] = [self.position]
        self.direction = START_DIRECTION
        self.next_direction = None
        self.body_color = SNAKE_COLOR
        self.last: Optional[Tuple[int, int]] = None

    def get_head_position(self) -> Tuple[int, int]:
        """Вернуть координаты головы."""
        return self.positions[0]

    def update_direction(self) -> None:
        """Обновить направление движения."""
        if self.next_direction:
            opposite = {UP: DOWN, DOWN: UP, LEFT: RIGHT, RIGHT: LEFT}

            if opposite.get(self.next_direction) != self.direction:
                self.direction = self.next_direction

        self.next_direction = None

    def move(self) -> None:
        """Переместить змейку."""
        head_x, head_y = self.get_head_position()
        dx, dy = self.direction

        new_head = (
            (head_x + dx * GRID_SIZE) % SCREEN_WIDTH,
            (head_y + dy * GRID_SIZE) % SCREEN_HEIGHT,
        )

        if self.length > 1 and new_head in self.positions[:-1]:
            self.reset()
            return

        self.positions.insert(0, new_head)

        if len(self.positions) > self.length:
            self.last = self.positions.pop()

    def draw(self, surface: pygame.Surface) -> None:
        """Отрисовать змейку."""
        if self.last:
            tail_rect = pygame.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(surface, BOARD_BACKGROUND_COLOR, tail_rect)

        for position in self.positions:
            self.draw_cell(surface, position)

    def reset(self) -> None:
        """Сбросить змейку."""
        self.length = 1
        self.positions = [CENTER_POSITION]
        self.direction = random.choice([UP, DOWN, LEFT, RIGHT])
        self.next_direction = None
        self.last = None


def handle_keys(snake: Snake) -> None:
    """Обработать нажатия клавиш."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                snake.next_direction = UP
            elif event.key == pygame.K_DOWN:
                snake.next_direction = DOWN
            elif event.key == pygame.K_LEFT:
                snake.next_direction = LEFT
            elif event.key == pygame.K_RIGHT:
                snake.next_direction = RIGHT
            elif event.key == pygame.K_ESCAPE:
                pygame.quit()
                raise SystemExit


def main() -> None:
    """Запустить игру."""
    pygame.init()

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('Изгиб Питона')

    clock = pygame.time.Clock()

    snake = Snake()
    apple = Apple(set(snake.positions))

    while True:
        handle_keys(snake)
        snake.update_direction()
        snake.move()

        if snake.get_head_position() == apple.position:
            snake.length += 1
            apple.randomize_position(set(snake.positions))

        screen.fill(BOARD_BACKGROUND_COLOR)
        apple.draw(screen)
        snake.draw(screen)
        pygame.display.update()
        clock.tick(GAME_SPEED)


if __name__ == '__main__':
    main()
