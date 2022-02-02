import pygame
from settings import *
from tile import Tile
from player import Player

class Level:
    def __init__(self):
        self.displaySurface = pygame.display.get_surface()
        self.visibleSprites = YSortCameraGroup()
        self.obstaclesSprites = pygame.sprite.Group()
        self.createMap()

    def createMap(self):
        for rowIndex, row in enumerate(WORLD_MAP):
            for colIndex, col in enumerate(row):
                x = colIndex * TILE_SIZE
                y = rowIndex * TILE_SIZE
                if col == 'x':
                    Tile((x, y), [self.visibleSprites, self.obstaclesSprites])
                if col == 'p':
                    self.player = Player((x, y), [self.visibleSprites], self.obstaclesSprites)

    def run(self):
        self.visibleSprites.customDraw(self.player)
        self.visibleSprites.update()

class YSortCameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.displaySurface = pygame.display.get_surface()
        self.halfWidth = self.displaySurface.get_size()[0] // 2
        self.halfHeight = self.displaySurface.get_size()[1] // 2
        self.offset = pygame.math.Vector2()

    def customDraw(self, player):
        self.offset.x = player.rect.centerx - self.halfWidth
        self.offset.y = player.rect.centery - self.halfHeight

        for sprite in sorted(self.sprites(), key = lambda sprite: sprite.rect.centery):
            offsetPosition = sprite.rect.topleft - self.offset
            self.displaySurface.blit(sprite.image, offsetPosition)