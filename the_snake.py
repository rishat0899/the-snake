from random import choice, randint

import pygame

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
SCREEN_CENTER = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
APPLE_MAX_CELL_INDEX_X = GRID_WIDTH - 1
APPLE_MAX_CELL_INDEX_Y = GRID_HEIGHT - 1

# Дополнительные параметры игрового окна
FLAGS = 0

# Глубина цвета
DEPTH = 32

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
SPEED = 10

# Настройка игрового окна:
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), FLAGS, DEPTH)

# Заголовок окна игрового поля:
pygame.display.set_caption('Змейка')

# Настройка времени:
clock = pygame.time.Clock()


class GameObject():
    """Базовый класс игровых объектов."""

    def __init__(self, position=SCREEN_CENTER, body_color=None):
        """Инициализируем базовые атрибуты объекта."""
        self.position = SCREEN_CENTER
        self.body_color = body_color

    def draw(self):
        """Метод отрисовки объектов.

        Обязательный для переопределения в дочерних классах.
        При вызове из родительского класса должен вызывать NotImplementedError.
        """
        raise NotImplementedError(
            'Метод draw() должен быть переопределен в дочернем классе'
        )


class Apple(GameObject):
    """Класс, описывающий яблоко и его логику."""

    def __init__(self, body_color=APPLE_COLOR, occupied_positions=None):
        """Инициализация яблока с заданным цветом и случайным положением."""
        super().__init__(position=None, body_color=body_color)
        # Устанавливаю случайное положение яблока
        self.randomize_position(occupied_positions)

    def randomize_position(self, occupied_positions=None):
        """Задаем яблоку новые случайные координаты, выровненные по сетке."""
        if occupied_positions is None:
            occupied_positions = []

        # Генерируем координаты до тех пор, пока не найдем свободную клетку
        while True:
            random_x = randint(0, APPLE_MAX_CELL_INDEX_X) * GRID_SIZE
            random_y = randint(0, APPLE_MAX_CELL_INDEX_Y) * GRID_SIZE
            new_position = (random_x, random_y)
            if new_position not in occupied_positions:
                self.position = new_position
                break

    def draw(self):
        """Отрисовка яблока."""
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


class Snake(GameObject):
    """Класс, описывающий змейку и ее логику."""

    def __init__(self, body_color=SNAKE_COLOR):
        """Инициализация змейки с начальными параметрами."""
        super().__init__(body_color=body_color)

        # Начальные атрибуты змейки
        self.reset()

    def get_head_position(self):
        """Возвращает координаты головы змейки."""
        return self.positions[0]

    def draw(self):
        """Отрисовка змейки"""
        # Отрисовка головы змейки
        head_rect = pygame.Rect(self.get_head_position(),
                                (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, head_rect)
        pygame.draw.rect(screen, BORDER_COLOR, head_rect, 1)

        # Затирание последнего сегмента
        if self.last:
            last_rect = pygame.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)

    def move(self):
        """Обновляет позицию змейки."""
        # Получаем текущую позицию головы
        head_pos_x, head_pos_y = self.get_head_position()

        # Получаем направление движения
        direction_x, direction_y = self.direction

        # Вычисляем новую позицию головы
        head_x_new = (head_pos_x + direction_x * GRID_SIZE) % SCREEN_WIDTH
        head_y_new = (head_pos_y + direction_y * GRID_SIZE) % SCREEN_HEIGHT
        head_position_new = (head_x_new, head_y_new)

        # Добавляем новую позицию головы в начало списка positions
        self.positions.insert(0, head_position_new)

        # Проверяем длину списка с длиной змейки
        if len(self.positions) > self.length:
            self.last = self.positions.pop()
        else:
            self.last = None

    def update_direction(self):
        """Определяем новое направление змейки."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def reset(self, is_start=True):
        """Сбрасываем змейку в начальное состояние."""
        # Сбрасываем длину змейку до одной клетки
        self.length = 1
        # Возвращаем змейку в центральную точку
        self.positions = [SCREEN_CENTER]
        # Выбираем начальное направление движения
        # Если начало игры, то направление вправо
        if is_start:
            self.direction = RIGHT
        # Если сброс, то случайное направление
        else:
            self.direction = choice([UP, DOWN, LEFT, RIGHT])
        # Убираем следующее направление
        self.next_direction = None
        # Очищаем след последнего сегмента
        self.last = None


def handle_keys(game_object):
    """Функция обработки действий пользователя."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pygame.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pygame.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pygame.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT


def main():
    """Основная функция запуска игры."""
    # Инициализация PyGame:
    pygame.init()

    # Создаем экземпляры объектов
    snake = Snake()
    apple = Apple(occupied_positions=snake.positions)

    # Очищаем экран
    screen.fill(BOARD_BACKGROUND_COLOR)

    while True:
        # Задаем скорость игры
        clock.tick(SPEED)

        # Обрабатываем нажатия клавиш
        handle_keys(snake)

        # Обновляем направление движения
        snake.update_direction()

        # Перемещаем змейку на одну ячейку
        snake.move()

        # Проверяем события:
        # Если координаты головы = координатам яблока,
        # Съесть яблоко и переместить яблоко на новую позицию
        if snake.get_head_position() == apple.position:
            snake.length += 1
            apple.randomize_position(snake.positions)

        # Если координаты головы = координатам других частей тела,
        # Сбросить змейку и очистить экран от остального тела
        elif snake.get_head_position() in snake.positions[1:]:
            snake.reset(is_start=False)
            screen.fill(BOARD_BACKGROUND_COLOR)

        # Отрисовываем объекты на новых позициях
        apple.draw()
        snake.draw()

        # Обновляем экран
        pygame.display.update()


if __name__ == '__main__':
    main()
