from random import choice, randint

import pygame
import datetime

# Рекорд прошлых игр:
try:
    with open('records.txt', 'r', encoding='UTF-8') as file:
        RECORD = int(file.readline().strip())
except (FileNotFoundError, ValueError):
    RECORD = 0

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет границы ячейки
BORDER_COLOR = (93, 216, 228)

# Цвет яблока
APPLE_COLOR = (255, 0, 0)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)

# Скорость движения змейки:
SPEED = 5

# Настройка игрового окна:
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pygame.display.set_caption(f'Змейка Максимальный рекорд: {RECORD}')

# Настройка времени:
clock = pygame.time.Clock()


class GameObject():
    """
    Класс для реализации игровых объектов, которые будут
    наследоваться от этого класса.

    Атрибуты:
    position (tuple) - Позиция объекта на экране
    body_color (tuple) - Цвет объекта
    """

    def __init__(self, body_color=None):
        self.position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.body_color = body_color

    def draw(self):
        """Функция-заглушка для переопределения в классах-наследниках"""
        pass


class Apple(GameObject):
    """
    Класс-наследник GameObject. Реализует создание и зарисовку объекта Яблоко.

    Атрибуты:
    position (tuple) - Позиция объекта на экране
    body_color (tuple) - Цвет объекта
    """

    def __init__(self):
        super().__init__(body_color=APPLE_COLOR)
        self.position = self.randomize_position()

    def randomize_position(self):
        """Возвращает случайную позицию объекта"""
        position_width = randint(0, GRID_WIDTH - 1) * GRID_SIZE
        position_height = randint(0, GRID_HEIGHT - 1) * GRID_SIZE
        return (position_width, position_height)

    def draw(self):
        """Рисует яблоко на экране"""
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


class Snake(GameObject):
    """
    Класс-наследник GameObject. Реализует создание и зарисовку объекта Змея.

    Атрибуты:
    position (tuple) - Позиция объекта на экране
    length (int) - Длина змейки
    positions (list) - Позиции частей змейки и её головы
    direction (tuple) - Текущие направление головы змейки
    next_direction (NoneType) - Следующие направление головы
    body_color (tuple) - Цвет объекта
    last (NoneType) - Хвост змеи
    """

    def __init__(self):
        super().__init__(body_color=SNAKE_COLOR)
        self.length = 1
        self.positions = [self.position]
        self.direction = RIGHT
        self.next_direction = None
        self.last = None

    def update_direction(self):
        """Обновляет направление змейки"""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def get_head_position(self):
        """Возвращает позицию головы змейки"""
        return self.positions[0]

    def grow(self):
        """Увеличивает длину змеи"""
        self.length += 1

    def move(self):
        """Обработка движения змейки"""
        current_head = self.get_head_position()
        if self.direction in [RIGHT, LEFT]:
            new_width = current_head[0] + GRID_SIZE * self.direction[0]

            if new_width >= SCREEN_WIDTH or new_width < 0:
                new_width = SCREEN_WIDTH - abs(new_width)

            new_position = (new_width, current_head[1])
            self.positions.insert(0, new_position)

            if self.length < len(self.positions):
                self.last = self.positions.pop()
        elif self.direction in [UP, DOWN]:
            new_height = current_head[1] + GRID_SIZE * self.direction[1]

            if new_height >= SCREEN_HEIGHT or new_height < 0:
                new_height = SCREEN_HEIGHT - abs(new_height)

            new_position = (current_head[0], new_height)
            self.positions.insert(0, new_position)

            if self.length < len(self.positions):
                self.last = self.positions.pop()

    def draw(self):
        """Рисует змейку"""
        for position in self.positions[:-1]:
            rect = (pygame.Rect(position, (GRID_SIZE, GRID_SIZE)))
            pygame.draw.rect(screen, self.body_color, rect)
            pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

        # Отрисовка головы змейки
        head_rect = pygame.Rect(self.positions[0], (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, head_rect)
        pygame.draw.rect(screen, BORDER_COLOR, head_rect, 1)

        # Затирание последнего сегмента
        if self.last:
            last_rect = pygame.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)

    def reset(self):
        """Возвращает змейку в исходное состояние после "самоукуса"."""
        self.positions = [self.position]
        self.length = 1
        self.direction = choice([RIGHT, LEFT, UP, DOWN])
        self.last = None


def handle_keys(game_object):
    """
    Функция обработки нажатий пользователя
    :param game_object: Игровой объект(класс)
    """
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                raise SystemExit
            if event.key == pygame.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pygame.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pygame.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pygame.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT


def set_max_record(game_object, current_record: int) -> int:
    """
    Возвращает максимальную длину змейки и записывает рекорд в файл

    :param game_object: Экземпляр змейки
    :param current_record: Текущий рекорд в игре
    :type current_record: int
    :return: Возвращает старый(если не был побит) или новый рекорд
    :rtype: int
    """
    if game_object.length > current_record:
        current_record = game_object.length

        with open('records.txt', 'w', encoding='UTF-8') as file:
            file.write(str(current_record) + '\n')
            file.write(f'Новый рекорд был установлен {datetime.datetime.now()}.'
                       f'Длина змейки была равна {current_record}!\n'
            )
        pygame.display.set_caption(f'Змейка Максимальный рекорд: {current_record}')
    return current_record


def main():
    """Главная логика игры"""
    global RECORD
    pygame.init()
    apple = Apple()
    snake = Snake()

    while True:
        clock.tick(SPEED)
        handle_keys(snake)
        snake.update_direction()
        snake.move()

        if snake.get_head_position() == apple.position:
            snake.grow()
            while apple.position in snake.positions:
                apple.position = apple.randomize_position()

        if snake.positions[0] in snake.positions[1:]:
            RECORD = set_max_record(snake, RECORD)
            snake.reset()
            screen.fill(BOARD_BACKGROUND_COLOR)

        apple.draw()
        snake.draw()
        pygame.display.update()


if __name__ == '__main__':
    main()

# Для запуска виртуального окружения в powershell для начала нужно выполнить это:
# Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
