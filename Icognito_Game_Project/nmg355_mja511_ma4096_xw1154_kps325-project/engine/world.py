# """
# This file is currently unused but implements a 
# coordinate system to better render the game
# """

# class Coord:

# 	class Direction:
# 			RIGHT = (1,0)
# 			LEFT = (-1,0)
# 			UP = (0,1)
# 			DOWN = (0,-1)


# 	def __init__(self, x=0, y=0):
# 		self.x = x
# 		self.y = y

# 	def inSameRow(self, coord):
# 		return self.x == coord.x

# 	def inSameCol(self, coord):
# 		return self.y = coord.y


# class World:
# 	def __init__(self, player, engine, x=0, y=0, gravity=-2):
# 		self.player = player
# 		self.engine = engine
# 		self.x = x
# 		self.y = y
# 		self.gravity = gravity


# 		# dicts of coord obj to character obj
# 		self.enemies = {} 
# 		self.objects = {}

# 	def render(self):
# 		pass