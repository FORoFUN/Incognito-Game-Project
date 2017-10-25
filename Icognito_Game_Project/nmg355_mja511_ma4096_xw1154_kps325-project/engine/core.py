try:
    import cairosvg
    SVG_ENABLED = True
except:
    SVG_ENABLED = False

import pygame, sys, logging, collections, time
from pygame.locals import *
from StringIO import StringIO
from Queue import Queue

class Engine(object):
    def __init__(self, width, height, title=''):
        self.width = width
        self.height = height
        self.title = title
        self.key_handlers = collections.defaultdict(list)
        self.events = Queue()
        self.started = False
        self.narrate = False
        self.narrate_text = ""
        # self.menu = Menu()

        pygame.init()
        self.surface = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption(self.title)

        self.clock = pygame.time.Clock()

        logging.debug('Initialized {}x{} engine'.format(self.width, self.height))

    def register_key_handler(self, key, handler):
        if key in self.key_handlers:
            self.key_handlers[key].append(handler)
        else:
            self.key_handlers[key] = [handler]

    def init(self, world):
        self.surface.fill((51,51,51))
        menu = Menu()
        menu.init(['Start','Quit'], self.surface)
        menu.draw()
        pygame.key.set_repeat(199,69)#(delay,interval)
        pygame.display.update()
        start = False
        while not start:
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_UP:
                        menu.draw(-1)
                    if event.key == K_DOWN:
                        menu.draw(1)
                    if event.key == K_RETURN:
                        if menu.get_position() == 0:
                            start = True
                        elif menu.get_position() == 1:
                            self.quit()
                    if event.key == K_ESCAPE:
                        pygame.display.quit()
                        sys.exit()
                    pygame.display.update()
                elif event.type == QUIT:
                    pygame.display.quit()
                    sys.exit()
            pygame.time.wait(8)
        self.start(world)


    def tick(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.quit()

        keys_down = pygame.key.get_pressed()
        for key in self.key_handlers.keys():
            if key < len(keys_down) and keys_down[key]: # WTF is K_LAST and why is it screwing this up???
                for handler in self.key_handlers[key]:
                    handler()

        pygame.display.update()
        self.clock.tick(60)

    def start(self, world):
        self.started = True

        pygame.draw.rect(world.background_image.surface, (0, 0, 0), (0, world.height-world.floor, world.width, world.floor))

        trophy = Image('resources/sprites/trophy.png')
        trophy.scale(0.5)

        world.background_image.surface.blit(trophy.surface, (world.width - 100, world.height - world.floor - trophy.height))

        world.medkit = Image('resources/sprites/medkit.png')
        world.medkit.scale(0.2)

        world.medkits = [(world.width / 3, world.height - world.floor - world.medkit.height),
                         (2 * (world.width / 3), world.height - world.floor - world.medkit.height)]

        cloak_text = pygame.font.SysFont(None, 36).render("Cloak Meter", 1, (255, 255, 255))

        while self.started:
            if self.narrate:
                self.surface.fill((0, 0, 0))
                win_text = pygame.font.SysFont(None, 200).render(self.narrate_text, 1, (255, 255, 255))
                self.surface.blit(win_text, (self.width/2 - (win_text.get_width()/2), self.height/2 - (win_text.get_height()/2)))
                self.tick()
            else:
                self.surface.fill((0, 0, 0))
                world.tick()
                world.render()

                # Render player cloak on top of everything else
                self.surface.blit(cloak_text,
                                  (30, self.height - 50 - 30 - 30))
                pygame.draw.rect(self.surface,
                                 (0, 0, 255),
                                 (30, self.height - 50 - 30, world.player.cloak*2, 50))
                self.tick()

                if world.player.x + world.player.width > world.width - 50:
                    self.putNarrative("You Win!")
                if world.player.cloak <= 0:
                    self.putNarrative("Game Over!")

                if self.narrate:
                    time.sleep(0.5)

    def putNarrative(self, text):
        self.narrate = True
        self.narrate_text = text

    def stop(self):
        self.started = False

    def quit(self):
        logging.info('Exiting')
        pygame.quit()
        sys.exit()


class Image(object):
    def __init__(self, img_path):
        self._path = img_path

        if self._path.lower().endswith('svg'):
            if SVG_ENABLED:
                logging.debug('Loading SVG at {}'.format(self._path))
                png = cairosvg.svg2png(url=self._path)
                self.surface = pygame.image.load(StringIO(png)).convert_alpha()
            else:
                logging.warning('SVG not supported: install cairosvg')
                raise TypeError("Not a supported image format: SVG")
        else:
            logging.debug('Loading raster image at {}'.format(self._path))
            self.surface = pygame.image.load(self._path).convert_alpha()

        self.width = self.surface.get_width()
        self.height = self.surface.get_height()

    def resize(self, width, height):
        self.surface = pygame.transform.scale(self.surface, (width, height))
        self.width = width
        self.height = height

    def scale(self, percent):
        new_width = int(self.width * percent)
        new_height = int(self.height * percent)

        self.resize(new_width, new_height)

class World(object):
    def __init__(self, background_image, player, engine, x=0, y=0, floor=0, gravity=-2):
        self.background_image = background_image
        self.player = player
        self.engine = engine
        self.x = x
        self.y = y

        self.width = self.background_image.width
        self.height = self.background_image.height

        self.floor = floor
        self.gravity = gravity

        self.enemies = []
        self.statics = []
        self.medkits = []

        self.move_player(0, 0)

    def move_player(self, dx, dy):
        self.player.x += dx
        self.player.y += dy

        # Prevent movement outside of the background
        if self.player.x < 0:
            logging.debug('Limiting player x- movement')
            self.player.x = 0
        elif self.player.x + self.player.width > self.width:
            logging.debug('Limiting player x+ movement')
            self.player.x = self.width - self.player.width

        if self.player.y < self.floor:
            logging.debug('Limiting player y- movement')
            self.player.y = self.floor
        if self.player.y + self.player.height > self.height:
            logging.debug('Limiting player y+ movement')
            self.player.y = self.height - self.player.height

        player_screen_x = self.player.x - self.x

        left_cutoff = self.engine.width*1/3
        right_cutoff = self.engine.width*2/3

        if player_screen_x < left_cutoff:
            logging.debug('Sliding left to match player')
            self.x = self.player.x - left_cutoff
        elif player_screen_x + self.player.width > right_cutoff:
            logging.debug('Sliding right to match player')
            self.x = self.player.x - right_cutoff + self.player.width

        if self.x < 0:
            logging.debug('Limiting background x- movement')
            self.x = 0
        elif self.x > self.width - self.engine.width:
            logging.debug('Limiting background x+ movement')
            self.x = self.width - self.engine.width


    def player_walk(self, direction):
        if self.player.visible:
            self.move_player(direction*self.player.speed, 0)
            if direction != self.player.facing:
                self.player.facing = direction
                self.player.image.surface = pygame.transform.flip(self.player.image.surface, True, False)

    def player_jump(self):
        if not self.player.jumping and self.player.visible:
            logging.debug('Jump')
            self.player.dy = -self.gravity * 15
            self.player.jumping = True
            self.player.y += self.player.dy

    def tick(self):
        if self.player.y > self.floor:
            logging.debug('In air')
            self.move_player(0, self.player.dy)
            self.player.dy += self.gravity

            if self.player.y <= self.floor:
                logging.debug('Landed')
                self.player.dy = 0
                self.player.jumping = False

        if pygame.key.get_pressed()[K_DOWN]:
            logging.debug('Hiding')
            self.player.visible = False
            self.player.cloak -= 0.5
        else:
            self.player.visible = True

        for static in self.statics:
            new_pos = static.colliding(self.player)
            if new_pos:
                logging.debug('Collision with player')
                if self.player.y != new_pos[1]:
                    self.player.dy = 0
                    self.player.jumping = False
                self.player.x = new_pos[0]
                self.player.y = new_pos[1]

        for enemy in self.enemies:
            enemy.move(self.player)
            if enemy.can_see(self.player):
                self.player_spotted(enemy)

    def player_spotted(self, enemy):
        logging.debug("Player spotted")
        if enemy.detected_image and enemy.image != enemy.detected_image:
            enemy.image = enemy.detected_image
        self.lose()

    def lose(self):
        self.engine.putNarrative("Game Over!")

    def render(self):
        # Render everything in its absolute position to a copy of the background
        abs_pos_surface = self.background_image.surface.copy()
        self.player.blit_to(abs_pos_surface)

        for static in self.statics:
            static.blit_to(abs_pos_surface)

        for enemy in self.enemies:
            enemy.blit_to(abs_pos_surface)
            if not self.player.visible:
                vision_end = enemy.x + enemy.facing * enemy.view_distance
                if (enemy.x > self.x or vision_end > self.x) and (enemy.x < self.x + self.width or vision_end < self.x + self.width):
                    enemy.blit_vision_to(abs_pos_surface)

        for coords in self.medkits:
            if self.player.x + self.player.width >= coords[0]:
                self.player.cloak += 50
                self.medkits.remove(coords)
            else:
                abs_pos_surface.blit(self.medkit.surface, coords)

        # Then blit the background on the screen where it needs to be
        self.engine.surface.blit(abs_pos_surface, (-self.x, self.y))


class StaticRect(object):
    def __init__(self, x, y, width, height, color=(255, 255, 255)):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color

    def colliding(self, player):
        # Static is below player
        if self.y < player.y <= self.y + self.height and (self.x < player.x < self.x+self.width or self.x < player.x+player.width < self.x+self.width):
            return (player.x, self.y+self.height)
        # Static is above player
        if self.y <= player.y + player.height < self.y + self.height and (self.x < player.x < self.x+self.width or self.x < player.x+player.width < self.x+self.width):
            return (player.x, self.y-player.height)
        # Static is left of player
        if self.x < player.x <= self.x + self.width and (self.y < player.y < self.y+self.height or self.y < player.y+player.height < self.y+self.height or player.y < self.y < player.y+player.height or player.y < self.y+self.height < player.y+player.height):
            return (self.x+self.width, player.y)
        # Static is right of player
        if self.x <= player.x + player.width < self.x + self.width and (self.y < player.y < self.y+self.height or self.y < player.y+player.height < self.y+self.height or player.y < self.y < player.y+player.height or player.y < self.y+self.height < player.y+player.height):
            return (self.x-player.width, player.y)


        return None

    def blit_to(self, surface):
        pygame.draw.rect(surface, self.color, (self.x, surface.get_height() - self.y - self.height, self.width, self.height), 0)

class Menu:
    lista = []
    pola = []
    title = None
    font_size = 32
    font_path = 'resources/font/coders_crux.ttf'
    font = pygame.font.Font
    dest_surface = pygame.Surface
    pol_count = 0
    background_color = (51,51,51)
    text_color =  (255, 255, 255)
    color_selection = (0,0,0)
    item_selection = 0
    position_paste = (0,0)
    menu_width = 0
    menu_height = 0

    class Title:
        text = ''
        box = pygame.Surface
        container = pygame.Rect

    class Pole:
        text = ''
        pole = pygame.Surface
        pole_rect = pygame.Rect
        selection_rect = pygame.Rect

    def move_menu(self, top, left):
        self.position_paste = (top,left)

    def set_colors(self, text, selection, background):
        self.background_color = background
        self.text_color =  text
        self.color_selection = selection

    def set_fontsize(self,font_size):
        self.font_size = font_size

    def set_font(self, path):
        self.font_path = path

    def get_position(self):
        return self.item_selection

    def init(self, lista, dest_surface):
        self.lista = lista
        self.dest_surface = dest_surface
        self.pol_count = len(self.lista)
        self.create_struct()

    def draw(self,move=0):
        if move:
            self.item_selection += move
            if self.item_selection == -1:
                self.item_selection = self.pol_count - 1
            self.item_selection %= self.pol_count
        menu = pygame.Surface((self.menu_width, self.menu_height))
        menu.fill(self.background_color)
        selection_rect = self.pola[self.item_selection].selection_rect
        pygame.draw.rect(menu,self.color_selection,selection_rect)

        menu.blit(self.title.box,self.title.container)

        for i in xrange(self.pol_count):
            menu.blit(self.pola[i].pole,self.pola[i].pole_rect)
        self.dest_surface.blit(menu,self.position_paste)
        return self.item_selection

    def create_struct(self):
        shift = 0
        self.menu_height = 0
        self.font = pygame.font.Font(self.font_path, self.font_size)

        self.title = self.Title()
        self.title.text = "Incognito"
        self.title.box = self.font.render(self.title.text, 1, self.text_color)
        self.title.container = self.title.box.get_rect()
        self.title.container.left = self.font_size * 0.5
        self.title.container.top = (self.font_size * 0.5) + ((self.font_size * 0.5) * 2 + self.title.container.height)

        for i in xrange(self.pol_count):
            self.pola.append(self.Pole())
            self.pola[i].text = self.lista[i]
            self.pola[i].pole = self.font.render(self.pola[i].text, 1, self.text_color)

            self.pola[i].pole_rect = self.pola[i].pole.get_rect()
            shift = int(self.font_size * 0.2)

            height = self.pola[i].pole_rect.height
            self.pola[i].pole_rect.left = shift
            self.pola[i].pole_rect.top = shift+(shift*2+height)*i

            width = self.pola[i].pole_rect.width+shift*2
            height = self.pola[i].pole_rect.height+shift*2
            left = self.pola[i].pole_rect.left-shift
            top = self.pola[i].pole_rect.top-shift

            self.pola[i].selection_rect = (left,top ,width, height)
            if width > self.menu_width:
                    self.menu_width = width
            self.menu_height += height
        x = self.dest_surface.get_rect().centerx - self.menu_width / 2
        y = self.dest_surface.get_rect().centery - self.menu_height / 2
        mx, my = self.position_paste
        self.position_paste = (x+mx, y+my)
