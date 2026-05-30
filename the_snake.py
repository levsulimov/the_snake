import random

import pygame
from typing import List, Optional, Set, Tuple

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


class GameObject:
    """Base class for all game objects."""

    def __init__(
        self,
        position: Tuple[int, int] = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    ):
        """Initialize game object."""
        self.position = position
        self.body_color = None

    def draw(self, surface: pygame.Surface) -> None:
        """Draw object on surface."""
        pass


class Apple(GameObject):
    """Apple class that snake eats."""

    def __init__(self, occupied_cells: Optional[Set[Tuple[int, int]]] = None):
        """Initialize apple."""
        super().__init__()
        self.body_color = APPLE_COLOR
        self.randomize_position(occupied_cells)

    def randomize_position(
        self,
        occupied_cells: Optional[Set[Tuple[int, int]]] = None
    ) -> None:
        """Set random position for apple."""
        if occupied_cells is None:
            occupied_cells = set()

        if len(occupied_cells) >= GRID_WIDTH * GRID_HEIGHT:
            self.position = (0, 0)
            return

        while True:
            x = random.randint(0, GRID_WIDTH - 1) * GRID_SIZE
            y = random.randint(0, GRID_HEIGHT - 1) * GRID_SIZE
            new_pos = (x, y)

            if new_pos not in occupied_cells:
                self.position = new_pos
                break

    def draw(self, surface: pygame.Surface) -> None:
        """Draw apple on surface."""
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(surface, self.body_color, rect)
        pygame.draw.rect(surface, BOARD_BACKGROUND_COLOR, rect, 1)


class Snake(GameObject):
    """Snake class controlled by player."""

    def __init__(self):
        """Initialize snake."""
        super().__init__()
        self.length = 1
        self.positions: List[Tuple[int, int]] = [self.position]
        self.direction = START_DIRECTION
        self.next_direction = None
        self.body_color = SNAKE_COLOR
        self.last: Optional[Tuple[int, int]] = None

    def update_direction(self) -> None:
        """Update snake direction."""
        if self.next_direction:
            opposite = {UP: DOWN, DOWN: UP, LEFT: RIGHT, RIGHT: LEFT}
            if opposite.get(self.next_direction) != self.direction:
                self.direction = self.next_direction
            self.next_direction = None

    def move(self) -> None:
        """Move snake one step."""
        head_x, head_y = self.get_head_position()
        dx, dy = self.direction

        new_head_x = (head_x + dx * GRID_SIZE) % SCREEN_WIDTH
        new_head_y = (head_y + dy * GRID_SIZE) % SCREEN_HEIGHT
        new_head = (new_head_x, new_head_y)

        if len(self.positions) >= self.length:
            self.last = self.positions[-1] if self.positions else None

        if self.length > 1 and new_head in self.positions[:-1]:
            self.reset()
            return

        self.positions.insert(0, new_head)

        if len(self.positions) > self.length:
            self.positions.pop()

        if self.positions and len(self.positions) <= self.length:
            if self.last == self.positions[-1]:
                self.last = None

    def draw(self, surface: pygame.Surface) -> None:
        """Draw snake on surface."""
        if self.last:
            last_rect = pygame.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(surface, BOARD_BACKGROUND_COLOR, last_rect)

        for pos in self.positions:
            rect = pygame.Rect(pos, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(surface, self.body_color, rect)
            pygame.draw.rect(surface, BOARD_BACKGROUND_COLOR, rect, 1)

    def get_head_position(self) -> Tuple[int, int]:
        """Return head position."""
        return self.positions[0] if self.positions else self.position

    def reset(self) -> None:
        """Reset snake to initial state."""
        self.length = 1
        self.positions = [self.position]
        self.direction = random.choice([UP, DOWN, LEFT, RIGHT])
        self.next_direction = None
        self.last = None


def handle_keys(snake: Snake) -> None:
    """Handle keyboard input."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
        elif event.type == pygame.KEYDOWN:
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
                quit()


def main() -> None:
    """Main game loop."""
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
