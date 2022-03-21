import pygame
from random import randint
from pathlib import Path

BLACK = (0, 0, 0)
MAX_SPEED = 30


class GameStatus:  # Статус игры, различные флаги
    def __init__(self):
        self.level_show = False
        self.rating_desk_show = False
        self.game_on = False
        self.rules_show = True
        self.start_game_button_show = True
        self.running = True


class Button(pygame.sprite.Sprite):  # Кнопка старта на первом экране
    def __init__(self, x, y, filename):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(filename).convert_alpha()
        self.rect = self.image.get_rect(center=(x, y))


class Ground(pygame.sprite.Sprite):  # Линия земли
    def __init__(self, y):
        super().__init__()
        self.add(horizontal_borders)
        self.image = pygame.Surface([width, 1])
        self.rect = pygame.Rect(0, y, width, 1)


class Tomato(pygame.sprite.Sprite):  # Томат
    def __init__(self, x, y, filename):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(filename).convert_alpha()
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = min(MAX_SPEED, 10 + level * 5)  # Скорость зависит от уровня, но есть ограничение
        self.fly = True

    def update(self):
        self.rect = self.rect.move(0, self.speed)

    def speed_up(self):
        self.speed += 5


class Hero(pygame.sprite.Sprite):  # Главный герой
    def __init__(self, sheet, columns, rows, x, y, direction):
        super().__init__()
        self.frames = []
        self.direction = 1  # 0 - влево, 1 - вправо
        self.cut_sheet(sheet, columns, rows, direction)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)
        self.speed = 0

    def cut_sheet(self, sheet, columns, rows, direction):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for i in range(columns):
            frame_location = (self.rect.w * i, self.rect.h * direction)
            self.frames.append(sheet.subsurface(pygame.Rect(
                frame_location, self.rect.size)))

    def update(self):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]
        if -10 < self.rect.x + self.speed < width - self.image.get_width() + 10:  # Не может заходить за границы экрана
            self.rect = self.rect.move(self.speed, 0)


def rule_showing():  # Показывает правила
    text_file = open('Rules.txt', 'r', encoding='utf-8')
    text = text_file.readlines()
    font = pygame.font.SysFont('arial', 16)
    row_step = 100
    for row in text:
        text_print = font.render(row.strip(), True, BLACK)
        screen.blit(text_print, (20, row_step))
        row_step += 30


def level_showing():  # Показывает уровень во время игры
    font = pygame.font.SysFont('arial', 30)
    if status.game_on:
        screen.blit(font.render(f'Уровень: {level}', True, BLACK), (50, 550))


def game_over():  # Финальное окно
    sad_tomato_img = pygame.image.load(Path("img/sad_tomato.png"))
    screen.blit(sad_tomato_img, (50, 360))
    font = pygame.font.SysFont('arial', 40)
    screen.blit(font.render('GAME OVER', True, BLACK), (130, 100))
    screen.blit(font.render(f'Ваш уровень: {level}', True, BLACK), (110, 150))
    screen.blit(font.render('Нажми Пробел', True, BLACK), (110, 250))


#  Задаем первоначальные настроки
width, height, fps, ground_level = 500, 600, 15, 500
default_speed = 10
level = 1
clock = pygame.time.Clock()
status = GameStatus()

pygame.init()
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Tomatos Catcher')
pygame.display.set_icon(pygame.image.load(Path("img/icon.png")))
background = pygame.image.load(Path("img/background.png"))
play_button = Button(width // 2, 400, Path('img/play_button.png'))
tomato = Tomato(randint(20, width - 20), 0, Path('img/tomato.png'))
horizontal_borders = pygame.sprite.Group()
ground = Ground(ground_level)
hero = Hero(pygame.image.load(Path("img/hero.png")), 8, 2, width // 2, 400, 1)

screen.blit(background, (0, 0))
clock = pygame.time.Clock()

while status.running:
    for even in pygame.event.get():
        if even.type == pygame.QUIT:
            status.running = False
        if even.type == pygame.MOUSEBUTTONDOWN and status.start_game_button_show:
            if b.collidepoint(pygame.mouse.get_pos()):  # Начинаем игру нажатием кнопки
                status.start_game_button_show = False
                status.rules_show = False
                status.game_on = True
                screen.blit(background, (0, 0))
        if (not status.game_on) and even.type == pygame.KEYDOWN:  # Начинаем игру нажатием пробела
            if even.key == pygame.K_SPACE:
                status.game_on = True
                level = 1
                tomato = Tomato(randint(20, width - 20), 0, Path('img/tomato.png'))
        if even.type == pygame.KEYDOWN:
            if even.key == pygame.K_LEFT:  # Герой идет налево
                hero = Hero(pygame.image.load(Path("img/hero.png")), 8, 2, hero.rect.x, 400, 1)
                hero.speed = - min(MAX_SPEED, default_speed + level * 5)
            elif even.key == pygame.K_RIGHT:  # Герой идет направо
                hero = Hero(pygame.image.load(Path("img/hero.png")), 8, 2, hero.rect.x, 400, 0)
                hero.speed = min(MAX_SPEED, default_speed + level * 5)
        if even.type == pygame.KEYUP:   # Кнопки движения не нажаты - останавливаемся
            hero.speed = 0

    if status.rules_show and (not status.game_on):  # Окно правил
        rule_showing()
    if status.start_game_button_show:  # Кнопка старта
        b = screen.blit(play_button.image, play_button.rect)
    if status.game_on:  # Игра
        screen.blit(background, (0, 0))
        screen.blit(tomato.image, tomato.rect)
        screen.blit(hero.image, hero.rect)
        tomato.update()
        hero.update()
        level_showing()
        if pygame.sprite.collide_mask(tomato, hero):  # Запускаем новую помидорку
            tomato = Tomato(randint(20, width - 20), 0, Path('img/tomato.png'))
            level += 1
        if pygame.sprite.spritecollideany(tomato, horizontal_borders):  # Помидорка упала
            game_over()
            tomato.speed = 0
            status.game_on = False
            status.rules_show = False
            status.start_game_button_show = False

    pygame.display.update()
    clock.tick(fps)
    pygame.display.flip()
