import pygame as pg, os, paths, sprites, math
from random import random, randrange
from gameobjects.player import Player
from gameobjects.map import Map
from gameobjects.shot import Shot
from gameobjects.powerup import Coffee, Mask, Heart

seeking_enemy_sprite_sheet = pg.image.load(os.path.join(paths.enemies_folder, 'seeking-enemy.png')).convert_alpha()
shooting_enemy_sprite_sheet = pg.image.load(os.path.join(paths.enemies_folder, 'shooting-enemy.png')).convert_alpha()
flying_enemy_sprite_sheet = pg.image.load(os.path.join(paths.enemies_folder, 'flying-enemy.png')).convert_alpha()
dissipating_enemy_sprite_sheet = pg.image.load(os.path.join(paths.enemies_folder, 'dissipating-enemy.png')).convert_alpha()
stumbling_enemy_sprite_sheet = pg.image.load(os.path.join(paths.enemies_folder, 'stumbling-enemy.png')).convert_alpha()
shot_sprite = pg.transform.scale(pg.image.load(os.path.join(paths.enemies_folder, 'enemy-shot.png')), (24, 24)).convert_alpha()

possible_angles = [0, 45, 90, 135, 180, -45, -90, -135, -180]
powerup_chance = 6


class SeekingEnemy(pg.sprite.Sprite):
    def __init__(self, player: Player, x, y):
        pg.sprite.Sprite.__init__(self)
        self.image = seeking_enemy_sprite_sheet
        self.imgs_corredor = []
        for i in range(7):
            img = seeking_enemy_sprite_sheet.subsurface((i * 32, 0), (32, 32))
            img = pg.transform.scale(img, (32 * 3, 32 * 3))
            self.imgs_corredor.append(img)

        self.index_lista = 0
        self.image = self.imgs_corredor[self.index_lista]
        self.rect = self.image.get_rect()
        self.hitbox = pg.Rect(0, 0, 17 * 3, 17 * 3)
        self.hitbox.center = self.rect.center
        self.mask = pg.mask.from_surface(self.image)
        self.acc = pg.Vector2(0, 0)
        self.rect.center = (x, y)
        self.player = player
        self.original_speed = 3
        self.speed = self.original_speed
        self.direction = 'right'

    def update(self):
        if self.index_lista > 6:
            self.index_lista = 0

        self.index_lista += 0.22
        self.image = self.imgs_corredor[int(self.index_lista)]

        self.move()

        self.rect.move_ip(self.speed * self.acc.x, self.speed * self.acc.y)
        self.hitbox.center = self.rect.center

        for syringe in sprites.all_syringes:
            if self.hitbox.colliderect(syringe):
                get_saved(self)
                syringe.kill()

    def move(self):
        dx = int(round(self.hitbox.centerx - self.player.hitbox.centerx))
        dy = int(round(self.hitbox.bottom - self.player.hitbox.bottom))

        self.acc.x = 0
        if dx > 0:
            self.acc.x = -1
            self.direction = 'left'
        elif dx < 0:
            self.acc.x = 1
            self.direction = 'right'
        else:
            self.direction = 'right'

        self.acc.y = 0
        if dy > 0:
            self.acc.y = -1
        elif dy < 0:
            self.acc.y = 1

        if dx != 0 and dy != 0:
            self.speed = int(round(self.original_speed * math.sqrt(2) / 2))
        else:
            self.speed = self.original_speed

        if self.direction == 'left':
            self.image = pg.transform.flip(self.image, True, False)


class ShootingEnemy(pg.sprite.Sprite):
    def __init__(self, player: Player, map: Map, x, y):
        pg.sprite.Sprite.__init__(self)
        self.image = shooting_enemy_sprite_sheet
        self.imgs_cuspidor = []
        for i in range(16):
            img = shooting_enemy_sprite_sheet.subsurface((i * 32, 0), (32, 32))
            img = pg.transform.scale(img, (32 * 3, 32 * 3))
            self.imgs_cuspidor.append(img)

        self.index_lista = 0
        self.image = self.imgs_cuspidor[self.index_lista]
        self.rect = self.image.get_rect()
        self.hitbox = pg.Rect(0, 0, 17 * 3, 23 * 3)
        self.mask = pg.mask.from_surface(self.image)
        self.rect.center = (x, y)
        self.shot_speed = 5
        self.shot_cooldown = 1000
        self.last_shot = pg.time.get_ticks()
        self.player = player
        self.map = map

    def update(self):
        if self.index_lista > 15:
            self.index_lista = 0
        
        self.index_lista += 0.18
        self.image = self.imgs_cuspidor[int(self.index_lista)]
        
        if self.index_lista >= 11:
            x = self.hitbox.centerx + 15
            y = self.hitbox.centery - 20
            dx = self.player.hitbox.centerx - x
            dy = self.player.hitbox.centery - y
            deg = math.degrees(math.atan2(-dy, dx))
            self.shoot(deg)

        self.hitbox.center = self.rect.center

        for syringe in sprites.all_syringes:
            if self.hitbox.colliderect(syringe):
                get_saved(self)
                syringe.kill()

    def shoot(self, angle):
        current_shot = pg.time.get_ticks()
        if current_shot - self.last_shot >= self.shot_cooldown:
            self.last_shot = current_shot
            shot = Shot(shot_sprite, self.hitbox.center, 15, -20, self.shot_speed, angle, self.map)
            sprites.all_enemy_shots.add(shot)
            sprites.all_sprites.add(shot)


class FlyingEnemy(pg.sprite.Sprite):
    def __init__(self, player: Player, x, y):
        pg.sprite.Sprite.__init__(self)
        self.image = flying_enemy_sprite_sheet
        self.imgs_baiacu = []
        for i in range(63):
            img = flying_enemy_sprite_sheet.subsurface((i * 32, 0), (32, 32))
            img = pg.transform.scale(img, (32 * 2, 32 * 2))
            self.imgs_baiacu.append(img)

        self.index_lista = 0
        self.image = self.imgs_baiacu[self.index_lista]
        self.rect = self.image.get_rect()
        self.hitbox = pg.Rect(0, 0, 17 * 3, 17 * 3)
        self.hitbox.center = self.rect.center
        self.mask = pg.mask.from_surface(self.image)
        self.acc = pg.Vector2(0, 0)
        self.rect.center = (x, y)
        self.player = player
        self.original_speed = 3
        self.speed = self.original_speed

    def update(self):
        if self.index_lista > 62:
            self.index_lista = 0

        self.index_lista += 0.7
        self.image = self.imgs_baiacu[int(self.index_lista)]

        self.move()

        self.rect.move_ip(self.speed * self.acc.x, self.speed * self.acc.y)
        self.hitbox.center = self.rect.center

        for syringe in sprites.all_syringes:
            if self.hitbox.colliderect(syringe):
                die(self)
                syringe.kill()

    def move(self):
        dx = int(round(self.hitbox.centerx - self.player.hitbox.centerx))
        dy = int(round(self.hitbox.bottom - self.player.hitbox.bottom))

        self.acc.x = 0
        if dx > 0:
            self.acc.x = -1
        elif dx < 0:
            self.acc.x = 1

        self.acc.y = 0
        if dy > 0:
            self.acc.y = -1
        elif dy < 0:
            self.acc.y = 1

        if dx != 0 and dy != 0:
            self.speed = int(round(self.original_speed * math.sqrt(2) / 2))
        else:
            self.speed = self.original_speed


class DissipatingEnemy(pg.sprite.Sprite):
    def __init__(self, player: Player, map: Map, x, y):
        pg.sprite.Sprite.__init__(self)
        self.image = dissipating_enemy_sprite_sheet
        self.imgs_dissipador = []
        for i in range(80):
            img = dissipating_enemy_sprite_sheet.subsurface((i * 32, 0), (32, 32))
            img = pg.transform.scale(img, (32 * 4, 32 * 4))
            self.imgs_dissipador.append(img)

        self.index_lista = 0
        self.image = self.imgs_dissipador[self.index_lista]
        self.rect = self.image.get_rect()
        self.hitbox = pg.Rect(0, 0, 23 * 4, 23 * 4)
        self.mask = pg.mask.from_surface(self.image)
        self.rect.center = (x, y)
        self.shot_speed = 5
        self.shot_cooldown = 1000
        self.last_shot = pg.time.get_ticks()
        self.player = player
        self.map = map

    def update(self):
        if self.index_lista > 79:
            self.index_lista = 0

        self.index_lista += 0.7
        self.image = self.imgs_dissipador[int(self.index_lista)]

        if self.index_lista >= 43:
            x = self.hitbox.centerx
            y = self.hitbox.centery
            dx = self.player.hitbox.centerx - x
            dy = self.player.hitbox.centery - y
            deg = math.degrees(math.atan2(-dy, dx))
            self.shoot(deg)

        self.hitbox.center = self.rect.center

        for syringe in sprites.all_syringes:
            if self.hitbox.colliderect(syringe):
                get_saved(self)
                syringe.kill()

    def shoot(self, angle):
        current_shot = pg.time.get_ticks()
        if current_shot - self.last_shot >= self.shot_cooldown:
            for i in range(-1, 2):
                self.last_shot = current_shot
                shot = Shot(shot_sprite, self.hitbox.center, 0, 0, self.shot_speed, min((possible_angles), key=lambda i:abs(i-angle)) + i * 20, self.map)
                sprites.all_enemy_shots.add(shot)
                sprites.all_sprites.add(shot)

class StumblingEnemy(pg.sprite.Sprite):
    def __init__(self, player: Player, x, y):
        pg.sprite.Sprite.__init__(self)
        self.image = stumbling_enemy_sprite_sheet
        self.imgs_tropego = []
        for i in range(11):
            img = stumbling_enemy_sprite_sheet.subsurface((i * 32, 0), (32, 32))
            img = pg.transform.scale(img, (32 * 6, 32 * 6))
            self.imgs_tropego.append(img)

        self.index_lista = 0
        self.image = self.imgs_tropego[self.index_lista]
        self.rect = self.image.get_rect()
        self.hitbox = pg.Rect(0, 0, 17 * 7, 17 * 7)
        self.hitbox.center = self.rect.center
        self.mask = pg.mask.from_surface(self.image)
        self.acc = pg.Vector2(0, 0)
        self.rect.center = (x, y)
        self.player = player
        self.original_speed = 2
        self.speed = self.original_speed
        self.direction = 'right'
        self.lives = 3

    def update(self):
        if self.index_lista > 10:
            self.index_lista = 0

        self.index_lista += 0.18
        self.image = self.imgs_tropego[int(self.index_lista)]

        self.move()

        self.rect.move_ip(self.speed * self.acc.x, self.speed * self.acc.y)
        self.hitbox.center = self.rect.center

        for syringe in sprites.all_syringes:
            if self.hitbox.colliderect(syringe):
                self.lives -= 1
                syringe.kill()
                if self.lives <= 0:
                    get_saved(self)

    def move(self):
        dx = int(round(self.hitbox.centerx - self.player.hitbox.centerx))
        dy = int(round(self.hitbox.bottom - self.player.hitbox.bottom))

        self.acc.x = 0
        if dx > 0:
            self.acc.x = -1
            self.direction = 'left'
        elif dx < 0:
            self.acc.x = 1
            self.direction = 'right'
        else:
            self.direction = 'right'

        self.acc.y = 0
        if dy > 0:
            self.acc.y = -1
        elif dy < 0:
            self.acc.y = 1

        if dx != 0 and dy != 0:
            self.speed = int(round(self.original_speed * math.sqrt(2) / 2))
        else:
            self.speed = self.original_speed

        if self.direction == 'left':
            self.image = pg.transform.flip(self.image, True, False)


def get_saved(enemy):
    i = randrange(1, powerup_chance)
    if i == 1:
        j = randrange(1, 4)
        if j == 1:
            powerup = Coffee(enemy.hitbox.centerx, enemy.hitbox.centery)
            sprites.all_powerups.add(powerup)
            sprites.all_sprites.add(powerup)
        elif j == 2:
            powerup = Mask(enemy.hitbox.centerx, enemy.hitbox.centery)
            sprites.all_powerups.add(powerup)
            sprites.all_sprites.add(powerup)
        elif j == 3:
            powerup = Heart(enemy.hitbox.centerx, enemy.hitbox.centery)
            sprites.all_powerups.add(powerup)
            sprites.all_sprites.add(powerup)

    sprites.saved += 1
    enemy.kill()

def die(enemy):
    i = randrange(1, powerup_chance)
    if i == 1:
        j = randrange(1, 3)
        if j == 1:
            powerup = Coffee(enemy.hitbox.centerx, enemy.hitbox.centery)
            sprites.all_powerups.add(powerup)
            sprites.all_sprites.add(powerup)
        elif j == 2:
            powerup = Mask(enemy.hitbox.centerx, enemy.hitbox.centery)
            sprites.all_powerups.add(powerup)
            sprites.all_sprites.add(powerup)
    
    enemy.kill()