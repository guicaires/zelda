import pygame
from entity import Entity
from support import *
from settings import *


class Player(Entity):
    def __init__(self, position, groups, obstaclesSprites, createAttack, destroyAttack, createMagic):
        super().__init__(groups)
        self.image = pygame.image.load('./src/img/player.png').convert_alpha()
        self.rect = self.image.get_rect(topleft=position)
        self.hitbox = self.rect.inflate(-6, HITBOX_OFFSET['player'])
        self.importPlayerAssets()
        self.status = 'down'
        self.attacking = False
        self.attackCooldown = 400
        self.atackTime = None
        self.obstaclesSprites = obstaclesSprites
        self.dead = False

        # weapon
        self.createAttack = createAttack
        self.destroyAttack = destroyAttack
        self.weaponIndex = 0
        self.weapon = list(WEAPON_DATA.keys())[self.weaponIndex]
        self.canSwitchWeapon = True
        self.weaponSwitchTime = None
        self.switchDurationCooldown = 200

        # magic
        self.createMagic = createMagic
        self.magicIndex = 0
        self.magic = list(MAGIC_DATA.keys())[self.magicIndex]
        self.canSwitchMagic = True
        self.magicSwitchTime = None

        # stats
        self.maxStats = {
            'health': 300,
            'energy': 140,
            'attack': 20,
            'magic': 10,
            'speed': 10
        }
        self.stats = {
            'health': 100,
            'energy': 60,
            'attack': 10,
            'magic': 4,
            'speed': 5
        }
        self.upgradeCost = {
            'health': 100,
            'energy': 100,
            'attack': 100,
            'magic': 100,
            'speed': 100
        }
        self.health = self.stats['health']
        self.energy = self.stats['energy']
        self.exp = 500

        # damage timer
        self.vulnerable = True
        self.hurtTime = None
        self.invunerabilityDuration = 500

        # import a sound
        self.weaponAttackSound = pygame.mixer.Sound('./src/audio/sword.wav')
        self.weaponAttackSound.set_volume(0.2)

    def importPlayerAssets(self):
        characterPath = './src/img/player/'
        self.animations = {
            'up': [], 'down': [], 'left': [], 'right': [],
            'right_idle': [], 'left_idle': [], 'up_idle': [], 'down_idle': [],
            'right_attack': [], 'left_attack': [], 'up_attack': [], 'down_attack': []
        }

        for animation in self.animations.keys():
            fullPath = characterPath + animation
            self.animations[animation] = importImagesFrom(fullPath)

    def input(self):
        if not self.attacking:
            keys = pygame.key.get_pressed()
            mouseKeys = pygame.mouse.get_pressed()

            if keys[pygame.K_UP] or keys[pygame.K_w]:
                self.direction.y = -1
                self.status = 'up'
            elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
                self.direction.y = 1
                self.status = 'down'
            else:
                self.direction.y = 0

            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.direction.x = -1
                self.status = 'left'
            elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.direction.x = 1
                self.status = 'right'
            else:
                self.direction.x = 0

            # weapon input
            if keys[pygame.K_j] or mouseKeys[0]:
                self.attacking = True
                self.atackTime = pygame.time.get_ticks()
                self.createAttack()
                self.weaponAttackSound.play()

            # magic input
            if keys[pygame.K_k] or mouseKeys[2]:
                self.attacking = True
                self.atackTime = pygame.time.get_ticks()
                style = list(MAGIC_DATA.keys())[self.magicIndex]
                strength = list(MAGIC_DATA.values())[
                    self.magicIndex]['strength'] + self.stats['magic']
                cost = list(MAGIC_DATA.values())[self.magicIndex]['cost']
                self.createMagic(style, strength, cost)

            if (keys[pygame.K_u] or keys[pygame.K_q]) and self.canSwitchWeapon:
                self.canSwitchWeapon = False
                self.weaponSwitchTime = pygame.time.get_ticks()

                if self.weaponIndex < len(list(WEAPON_DATA.keys())) - 1:
                    self.weaponIndex += 1
                else:
                    self.weaponIndex = 0

                self.weapon = list(WEAPON_DATA.keys())[self.weaponIndex]

            if (keys[pygame.K_i] or keys[pygame.K_e]) and self.canSwitchMagic:
                self.canSwitchMagic = False
                self.magicSwitchTime = pygame.time.get_ticks()

                if self.magicIndex < len(list(MAGIC_DATA.keys())) - 1:
                    self.magicIndex += 1
                else:
                    self.magicIndex = 0

                self.magic = list(MAGIC_DATA.keys())[self.magicIndex]

    def setStatus(self):
        if self.direction.x == 0 and self.direction.y == 0:
            if not 'idle' in self.status and not 'attack' in self.status:
                self.status = self.status + '_idle'

        if self.attacking:
            self.direction.x = 0
            self.direction.y = 0
            if not 'attack' in self.status:
                if 'idle' in self.status:
                    self.status = self.status.replace('_idle', '_attack')
                else:
                    self.status = self.status + '_attack'
        else:
            if 'attack' in self.status:
                self.status = self.status.replace('_attack', '')

    def cooldowns(self):
        currentTime = pygame.time.get_ticks()
        if self.attacking:
            if currentTime - self.atackTime >= self.attackCooldown + WEAPON_DATA[self.weapon]['cooldown']:
                self.attacking = False
                self.destroyAttack()

        if not self.canSwitchWeapon:
            if currentTime - self.weaponSwitchTime >= self.switchDurationCooldown:
                self.canSwitchWeapon = True

        if not self.canSwitchMagic:
            if currentTime - self.magicSwitchTime >= self.switchDurationCooldown:
                self.canSwitchMagic = True

        if not self.vulnerable:
            if currentTime - self.hurtTime >= self.invunerabilityDuration:
                self.vulnerable = True

    def animate(self):
        animation = self.animations[self.status]

        self.frameIndex += self.animationSpeed
        if self.frameIndex >= len(animation):
            self.frameIndex = 0

        self.image = animation[int(self.frameIndex)]
        self.rect = self.image.get_rect(center=self.hitbox.center)

        if not self.vulnerable:
            alpha = self.waveValue()
        else:
            alpha = 255
        self.image.set_alpha(alpha)

    def getFullWeaponDamage(self):
        baseDamage = self.stats['attack']
        weaponDamage = WEAPON_DATA[self.weapon]['damage']
        return baseDamage + weaponDamage

    def getFullMagicDamage(self):
        baseDamage = self.stats['magic']
        magicDamage = MAGIC_DATA[self.magic]['strength']
        return baseDamage + magicDamage

    def energyRecovery(self):
        if self.energy < self.stats['energy']:
            self.energy += 0.01 * self.stats['magic']

    def getStatsValueByIndex(self, index):
        return list(self.stats.values())[index]

    def getCostByIndex(self, index):
        return list(self.upgradeCost.values())[index]

    def checkDeath(self):
        if self.health <= 0:
            self.dead = True

    def update(self):
        self.input()
        self.cooldowns()
        self.setStatus()
        self.animate()
        self.energyRecovery()
        self.move(self.stats['speed'])
        self.checkDeath()
