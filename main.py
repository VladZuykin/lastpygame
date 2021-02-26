import pygame
import sys
import os

FPS = 50

RES = WIDTH, HEIGHT = 800, 600


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    intro_text = ["ЗАСТАВКА", "", "Правила игры:", "1. Нет правил"]

    fon = pygame.transform.scale(load_image('fon.jpg'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, True, pygame.Color('black'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                return
        pygame.display.flip()
        clock.tick(FPS)


def load_level(filename):
    filename = "data/" + filename
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile.readlines()]

    max_width = max(map(len, level_map))

    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


def generate_level(level):
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', x, y)
            elif level[y][x] == '#':
                Tile('wall', x, y)
            elif level[y][x] == '@':
                Tile('empty', x, y)
                new_player = Player(x, y)
    return new_player, len(level[0]), len(level)


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        if tile_type == "wall":
            walls_group.add(self)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = player_image
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = tile_width * pos_x + 15, tile_height * pos_y + 5

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy
        if pygame.sprite.spritecollideany(self, walls_group):
            self.rect.x -= dx
            self.rect.y -= dy
            return False
        return True


class Camera:
    def __init__(self, target, sprites):
        dx = WIDTH // 2 - target.rect.x - target.rect.w // 2
        dy = HEIGHT // 2 - target.rect.y - target.rect.h // 2

        for sprite in sprites:
            sprite.rect.x += dx
            sprite.rect.y += dy

    def update(self, dx, dy, sprites):
        for sprite in sprites:
            sprite.rect.x -= dx
            sprite.rect.y -= dy


class TileSprites(pygame.sprite.Group):
    def __init__(self):
        super().__init__()

    def my_draw(self, screen):
        self.draw(screen)
        for i in (-1, 0, 1):
            for j in (-1, 0, 1):
                if not (i == j == 0):
                    for sprite in self:
                        sprite_x = sprite.rect.x + i * tile_width * level_x
                        sprite_y = sprite.rect.y + j * tile_height * level_y
                        screen.blit(sprite.image, (sprite_x, sprite_y))


if __name__ == '__main__':
    level_file_name = input()
    if not os.path.exists("data/" + level_file_name):
        print("Такого файла не существует.")
    else:
        pygame.init()
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        screen.fill((0, 0, 0))
        pygame.display.set_caption("Марио v2")

        clock = pygame.time.Clock()

        tile_images = {'wall': load_image('box.png'), 'empty': load_image('grass.png')}
        player_image = load_image('mario.png')

        tile_width = tile_height = 50

        all_sprites = pygame.sprite.Group()
        tiles_group = TileSprites()
        walls_group = pygame.sprite.Group()
        player_group = pygame.sprite.Group()

        level = load_level(level_file_name)

        player, level_x, level_y = generate_level(level)

        start_screen()

        camera = Camera(player, all_sprites)
        running = True
        while running:
            screen.fill((0, 0, 0))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_DOWN, pygame.K_UP, pygame.K_LEFT, pygame.K_RIGHT):
                        dx, dy = 0, 0
                        if event.key == pygame.K_DOWN:
                            dx, dy = 0, 50
                        elif event.key == pygame.K_UP:
                            dx, dy = 0, -50
                        elif event.key == pygame.K_LEFT:
                            dx, dy = -50, 0
                        elif event.key == pygame.K_RIGHT:
                            dx, dy = 50, 0
                        if player.move(dx, dy):
                            camera.update(dx, dy, all_sprites)

            tiles_group.my_draw(screen)
            player_group.draw(screen)
            pygame.display.flip()
        pygame.quit()
