import random
from typing import Optional, Tuple

import pygame


# Константы игры
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Направления движения
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)


class GameObject:
    """
    Базовый класс для всех игровых объектов.
    
    Атрибуты:
        position (Tuple[int, int]): Координаты объекта на игровом поле.
        body_color (Tuple[int, int, int]): Цвет объекта в формате RGB.
    """
    
    def __init__(self, position: Optional[Tuple[int, int]] = None,
                 body_color: Optional[Tuple[int, int, int]] = None) -> None:
        """
        Инициализирует игровой объект.
        
        Args:
            position: Начальная позиция объекта. Если None - центр экрана.
            body_color: Цвет объекта. Если None - не задан.
        """
        self.position = position if position is not None else (
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        )
        self.body_color = body_color
    
    def draw(self, surface: pygame.Surface) -> None:
        """
        Отрисовывает объект на игровой поверхности.
        
        Args:
            surface: Игровая поверхность для отрисовки.
        """
        pass


class Apple(GameObject):
    """
    Класс яблока для игры "Змейка".
    
    Наследует от GameObject.
    """
    
    def __init__(self) -> None:
        """Инициализирует яблоко со случайной позицией и красным цветом."""
        super().__init__()
        self.body_color = (255, 0, 0)  # Красный цвет
        self.randomize_position()
    
    def randomize_position(self) -> None:
        """Устанавливает случайную позицию для яблока в пределах игрового поля."""
        x = random.randint(0, GRID_WIDTH - 1) * GRID_SIZE
        y = random.randint(0, GRID_HEIGHT - 1) * GRID_SIZE
        self.position = (x, y)
    
    def draw(self, surface: pygame.Surface) -> None:
        """
        Отрисовывает яблоко на игровой поверхности.
        
        Args:
            surface: Игровая поверхность для отрисовки.
        """
        rect = pygame.Rect(
            (self.position[0], self.position[1]),
            (GRID_SIZE, GRID_SIZE)
        )
        pygame.draw.rect(surface, self.body_color, rect)
        pygame.draw.rect(surface, (255, 255, 255), rect, 1)


class Snake(GameObject):
    """
    Класс змейки для игры "Змейка".
    
    Наследует от GameObject.
    
    Атрибуты:
        length (int): Текущая длина змейки.
        positions (list[Tuple[int, int]]): Список позиций сегментов змейки.
        direction (Tuple[int, int]): Текущее направление движения.
        next_direction (Optional[Tuple[int, int]]): Следующее направление.
        last (Optional[Tuple[int, int]]): Позиция последнего удалённого сегмента.
    """
    
    def __init__(self) -> None:
        """Инициализирует змейку в начальном состоянии."""
        super().__init__()
        self.body_color = (0, 255, 0)  # Зелёный цвет
        self.length = 1
        self.positions = [self.position]
        self.direction = RIGHT
        self.next_direction = None
        self.last = None
    
    def update_direction(self) -> None:
        """
        Обновляет направление движения змейки.
        
        Если было задано следующее направление (next_direction),
        обновляет текущее направление.
        """
        if self.next_direction:
            # Проверка, чтобы змейка не могла развернуться на 180 градусов
            current_x, current_y = self.direction
            next_x, next_y = self.next_direction
            if (current_x + next_x != 0) or (current_y + next_y != 0):
                self.direction = self.next_direction
            self.next_direction = None
    
    def get_head_position(self) -> Tuple[int, int]:
        """
        Возвращает позицию головы змейки.
        
        Returns:
            Координаты головы змейки.
        """
        return self.positions[0]
    
    def move(self) -> None:
        """
        Обновляет позицию змейки, добавляя новую голову и удаляя хвост.
        
        Также проверяет столкновение змейки с самой собой.
        """
        # Получаем текущую позицию головы
        head_x, head_y = self.get_head_position()
        
        # Вычисляем новую позицию головы
        dir_x, dir_y = self.direction
        new_x = (head_x + dir_x * GRID_SIZE) % SCREEN_WIDTH
        new_y = (head_y + dir_y * GRID_SIZE) % SCREEN_HEIGHT
        new_position = (new_x, new_y)
        
        # Проверяем столкновение с собой
        if new_position in self.positions[1:]:
            self.reset()
            return
        
        # Добавляем новую позицию в начало списка
        self.positions.insert(0, new_position)
        
        # Сохраняем последнюю позицию для стирания
        self.last = self.positions[-1]
        
        # Если длина змейки больше текущего размера, удаляем последний элемент
        if len(self.positions) > self.length:
            self.positions.pop()
    
    def reset(self) -> None:
        """Сбрасывает змейку в начальное состояние."""
        self.length = 1
        self.positions = [self.position]
        self.direction = RIGHT
        self.next_direction = None
        self.last = None
    
    def draw(self, surface: pygame.Surface) -> None:
        """
        Отрисовывает змейку на игровой поверхности.
        
        Args:
            surface: Игровая поверхность для отрисовки.
        """
        # Стираем последний удалённый сегмент
        if self.last:
            last_rect = pygame.Rect(
                (self.last[0], self.last[1]),
                (GRID_SIZE, GRID_SIZE)
            )
            pygame.draw.rect(surface, BOARD_BACKGROUND_COLOR, last_rect)
        
        # Отрисовываем все сегменты змейки
        for i, pos in enumerate(self.positions):
            rect = pygame.Rect(
                (pos[0], pos[1]),
                (GRID_SIZE, GRID_SIZE)
            )
            pygame.draw.rect(surface, self.body_color, rect)
            pygame.draw.rect(surface, (255, 255, 255), rect, 1)
            
            # Отрисовываем глаза на голове
            if i == 0:
                eye_size = GRID_SIZE // 5
                # Определяем позиции глаз в зависимости от направления
                if self.direction == RIGHT:
                    left_eye = (pos[0] + GRID_SIZE - eye_size * 2,
                                pos[1] + eye_size * 2)
                    right_eye = (pos[0] + GRID_SIZE - eye_size * 2,
                                 pos[1] + GRID_SIZE - eye_size * 2)
                elif self.direction == LEFT:
                    left_eye = (pos[0] + eye_size,
                                pos[1] + eye_size * 2)
                    right_eye = (pos[0] + eye_size,
                                 pos[1] + GRID_SIZE - eye_size * 2)
                elif self.direction == UP:
                    left_eye = (pos[0] + eye_size * 2,
                                pos[1] + eye_size)
                    right_eye = (pos[0] + GRID_SIZE - eye_size * 2,
                                 pos[1] + eye_size)
                else:  # DOWN
                    left_eye = (pos[0] + eye_size * 2,
                                pos[1] + GRID_SIZE - eye_size * 2)
                    right_eye = (pos[0] + GRID_SIZE - eye_size * 2,
                                 pos[1] + GRID_SIZE - eye_size * 2)
                
                pygame.draw.circle(surface, (0, 0, 0), left_eye, eye_size)
                pygame.draw.circle(surface, (0, 0, 0), right_eye, eye_size)


def handle_keys(snake: Snake) -> None:
    """
    Обрабатывает нажатия клавиш для управления змейкой.
    
    Args:
        snake: Объект змейки, направление которой нужно изменить.
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                snake.next_direction = UP
            elif event.key == pygame.K_DOWN:
                snake.next_direction = DOWN
            elif event.key == pygame.K_LEFT:
                snake.next_direction = LEFT
            elif event.key == pygame.K_RIGHT:
                snake.next_direction = RIGHT


def main() -> None:
    """Основная функция игры, содержащая главный игровой цикл."""
    # Инициализация Pygame
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('Изгиб Питона')
    clock = pygame.time.Clock()
    
    # Создание игровых объектов
    snake = Snake()
    apple = Apple()
    
    # Главный игровой цикл
    while True:
        # Обработка событий
        handle_keys(snake)
        
        # Обновление направления змейки
        snake.update_direction()
        
        # Движение змейки
        snake.move()
        
        # Проверка, съела ли змейка яблоко
        if snake.get_head_position() == apple.position:
            snake.length += 1
            apple.randomize_position()
            
            # Убедимся, что яблоко не появляется на змейке
            while apple.position in snake.positions:
                apple.randomize_position()
        
        # Очистка экрана
        screen.fill(BOARD_BACKGROUND_COLOR)
        
        # Отрисовка объектов
        apple.draw(screen)
        snake.draw(screen)
        
        # Обновление экрана
        pygame.display.update()
        
        # Ограничение FPS
        clock.tick(20)


if __name__ == '__main__':
    main()
