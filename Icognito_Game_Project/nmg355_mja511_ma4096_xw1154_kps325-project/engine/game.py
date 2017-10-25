from core import *
import characters

logging.basicConfig(level=logging.WARNING)

game = Engine(1280, 720, '1122 Game')
game.register_key_handler(ord('q'), lambda: game.quit())

player_img = Image('resources/sprites/player.png')
player_img.scale(0.25)

player = characters.Player(player_img)

world = World(Image('resources/background_images/bkg.png'), player, game, floor=200)

game.register_key_handler(K_UP, lambda: world.player_jump())
game.register_key_handler(K_LEFT, lambda: world.player_walk(characters.Direction.LEFT))
game.register_key_handler(K_RIGHT, lambda: world.player_walk(characters.Direction.RIGHT))

enemy_image = Image('resources/sprites/enemy.png')
enemy_image.scale(0.25)

enemy_detected_image = Image('resources/sprites/enemy_detected.png')
enemy_detected_image.scale(0.25)

for i in range(2, 10, 2):
    world.enemies.append(characters.PatrollingEnemy(enemy_image, x=1000*i, y=200, detected_image=enemy_detected_image))


# while True:
#     game.surface.fill((0,0,0))
#     world.tick()
#     world.render()
#     world.background_image.surface.blit(trophy.surface, (world.width - 100, world.height - world.floor - trophy.height))
#     game.tick()
#     if player.x + player.width > world.width - 50:
#         break

# n = 0
# while True:
#     game.surface.fill((0,0,0))
#     font = pygame.font.SysFont(None, n)
#     win_text = font.render("You win!", 1, (255,255,255))
#     game.surface.blit(win_text, (game.width/2 - (win_text.get_width()/2), game.height/2 - (win_text.get_height()/2)))
#     game.tick()
#     if n < 300:
#         n += 1


# surface = pygame.display.set_mode((854,480)) #0,6671875 and 0,(6) of HD resoultion
# surface.fill((51,51,51))
# menu = Menu()
# menu.init(['Start','Quit'], surface)
# menu.draw()

game.init(world)
