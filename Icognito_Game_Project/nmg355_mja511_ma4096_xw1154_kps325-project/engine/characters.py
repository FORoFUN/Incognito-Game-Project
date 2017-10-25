import pygame

class Direction(object):
    LEFT = -1
    RIGHT = 1

class Character(object):
    def __init__(self, image, x=0, y=0, speed=7):
        self.image = image
        self.x = x
        self.y = y
        self.speed = speed
        self.facing = Direction.LEFT
        self.jumping = False
        self.dy = 0
        
        self.width = self.image.width
        self.height = self.image.height
    
    def blit_to(self, surface):
        surface.blit(self.image.surface, (self.x, surface.get_height() - self.y - self.height))


class Player(Character):
    def __init__(self, image, x=0, y=0):
        Character.__init__(self, image, x, y, speed=15)
        self.facing = Direction.RIGHT
        self.visible = True
        self.transparent_surface = pygame.Surface((self.width, self.height))
        self.transparent_surface.set_colorkey((0,0,0))
        self.cloak = 100.0

    def blit_to(self, surface):
        self.transparent_surface.fill((0,0,0))
        self.transparent_surface.blit(self.image.surface, (0,0))
        self.transparent_surface.set_alpha(50 if not self.visible else 255)
        surface.blit(self.transparent_surface, (self.x, surface.get_height() - self.y - self.height))


class Enemy(Character):
    def __init__(self, image, x=0, y=0, speed=7, view_distance=200, detected_image=None):
        Character.__init__(self, image, x, y, speed)
        self.view_distance = view_distance
        self.detected_image = detected_image
        self.normal_image = image

    def can_see(self, player):
        if player.visible:
            if abs(player.y - self.y) < 60:
                if self.facing == Direction.LEFT:
                    return (
                            player.x < self.x and
                            player.x > self.x - self.view_distance
                        ) or (
                            player.x + player.width < self.x and
                            player.x + player.width > self.x - self.view_distance
                        )
                elif self.facing == Direction.RIGHT:
                    return (
                            player.x > self.x and
                            player.x < self.x + self.view_distance
                        ) or (
                            player.x + player.width > self.x and
                            player.x + player.width < self.x + self.view_distance
                        )
        if self.image != self.normal_image:
            self.image = self.normal_image
        return False

    def blit_vision_to(self, surface):
        pygame.draw.rect(
            surface,
            (255, 0, 0), # Color
            [
                self.x+self.width*(self.facing==Direction.RIGHT), # x-coord
                surface.get_height() - self.y, # y-coord
                self.view_distance*self.facing, # width
                -1*self.height # height
            ],
            10) # width

    def move(self, player): # abstract
        raise NotImplementedError()


class PatrollingEnemy(Enemy):
    def __init__(self, image, x=0, y=0, speed=7, view_distance=300, patrol_distance=300, detected_image=None):
        Enemy.__init__(self, image, x, y, speed, view_distance, detected_image)
        self.patrol_area_left = x
        self.patrol_area_right = x + patrol_distance

    def move(self, player):
        if self.x < self.patrol_area_left or self.x > self.patrol_area_right + self.width:
            self.image.surface = pygame.transform.flip(self.image.surface, True, False)
            self.facing *= -1
        self.x += self.facing * self.speed
