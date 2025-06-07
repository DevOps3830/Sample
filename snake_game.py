import random
import os
import time

WIDTH = 20
HEIGHT = 10

RIGHT = (0, 1)
LEFT = (0, -1)
UP = (-1, 0)
DOWN = (1, 0)

DIRECTIONS = [RIGHT, DOWN, LEFT, UP]


def clear_screen():
    os.system('clear')


def print_board(snake, food):
    for y in range(HEIGHT + 2):
        row = ''
        for x in range(WIDTH + 2):
            if y == 0 or y == HEIGHT + 1 or x == 0 or x == WIDTH + 1:
                row += '#'
            elif (y - 1, x - 1) == snake[0]:
                row += 'O'
            elif (y - 1, x - 1) in snake[1:]:
                row += 'o'
            elif (y - 1, x - 1) == food:
                row += '*'
            else:
                row += ' '
        print(row)
    print('Snake length:', len(snake))


def place_food(snake):
    while True:
        pos = (random.randint(0, HEIGHT - 1), random.randint(0, WIDTH - 1))
        if pos not in snake:
            return pos


def move_snake(snake, direction, food):
    head = (snake[0][0] + direction[0], snake[0][1] + direction[1])
    if head[0] < 0 or head[0] >= HEIGHT or head[1] < 0 or head[1] >= WIDTH:
        return False, snake, food
    if head in snake:
        return False, snake, food
    snake.insert(0, head)
    if head == food:
        food = place_food(snake)
    else:
        snake.pop()
    return True, snake, food


def main():
    snake = [(HEIGHT // 2, WIDTH // 2)]
    food = place_food(snake)
    direction_index = 0
    steps = 0
    clear_screen()
    while steps < 30:
        direction = DIRECTIONS[direction_index % len(DIRECTIONS)]
        alive, snake, food = move_snake(snake, direction, food)
        clear_screen()
        print_board(snake, food)
        if not alive:
            print('Game over!')
            break
        steps += 1
        if steps % 7 == 0:
            direction_index += 1
        time.sleep(0.3)
    else:
        print('Demo finished!')


if __name__ == '__main__':
    main()
