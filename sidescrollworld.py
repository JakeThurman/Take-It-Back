"""
	Defines Elements for the scroll game.
"""

import pygame, random, lineofsight
from rendering import Sprite

class WallOpenDir:
	# "Enum" constant values.
	NONE = 0
	LEFT_ONLY = 1
	RIGHT_ONLY = 2
	UP_ONLY = 3
	DOWN_ONLY = 4
	
	# Gets a file image from a wall direction
	def get_file_name(dir):
		# We start with a map object...
		map = {
			WallOpenDir.NONE: "wall/wall.png",
			WallOpenDir.LEFT_ONLY: "wall/left_only.png",
			WallOpenDir.RIGHT_ONLY: "wall/right_only.png",
			WallOpenDir.UP_ONLY: "wall/up_only.png",
			WallOpenDir.DOWN_ONLY: "wall/down_only.png",
		}
		# Then return the needed value.
		return map[dir]
		
	# Returns a WallOpenDir value from a letter key
	def of(letter):
		# Maps .map file characters to the appropriate direction...
		map = {
			"R": WallOpenDir.RIGHT_ONLY,
			"L": WallOpenDir.LEFT_ONLY,
			"D": WallOpenDir.DOWN_ONLY,
			"U": WallOpenDir.UP_ONLY,
			"X": WallOpenDir.NONE
		}
	
		# Then return the needed value.
		return map[letter];
			
class Wall(Sprite):
	'''
		Class for wall blocks
		.map file: X, L, R, U, D (with appropriate dirrection)
	'''
	def __init__(self, x, y, dir):
		# Init the parent class
		super().__init__(x, y, WallOpenDir.get_file_name(dir))

		# Store size info about the sprite
		self.dir = dir

class WinBlock(Sprite):
	"""
		Class for "end-game"/"win" blocks 
		.map file: W
	"""
	def __init__(self, x, y):
		# Init the parent class
		super().__init__(x, y, "wall/win_block.png")
		
class Spawner(Sprite):
	"""
		Class for weapon blacks 
		.map file 0-9
	"""	
	def __init__(self, x, y, power):
		# Init the parent class
		super().__init__(x, y, "wall/weapon.png", use_alpha=True)
		# Don't let users pass through these blocks
		self.dir = WallOpenDir.NONE
		# Store the power
		self.power = power
		# Store the fire interval
		self.min_fire_interval = 80 * (10 - power)
		# Say that we are halfway through our wait to fire initially.
		self.last_fire_ticks = (self.min_fire_interval / 2)
	
	def update(self, refresh_time, player, world, add_entity_func):
		# Increment the wait counter with the time since the last update
		self.last_fire_ticks += refresh_time
		
		# If we haven't waited long enough, we don't want to fire. Then, check 
		# a randomly generated integer in the range [0, 10 * (10 - power)]; if
		# that randomly returns 1, we want to fire
		should_fire = self.last_fire_ticks > self.min_fire_interval and random.randint(0, 10 * (10 - self.power)) == 1;
		
		# If the random number genderation says we should shoot, and we can see the player, shoot!
		if should_fire:
			dir = lineofsight.get_direction(player, self, world)
			
			if dir != lineofsight.CANT_SEE:
				is_right = dir == lineofsight.RIGHT
				add_entity_func(Bullet(self.rect.right if is_right else self.rect.left, self.rect.center[1], is_right, self, self.power))
				self.last_fire_ticks = 0 # Reset the wait counter
		
class Bullet(Sprite):	
	"""
		Faster than a speeding bullet...
		Wait... a moving bullet class.
		As shot by a "spawner" weapon
	"""
	# Constants
	HORIZ_MOV_INCR = 10
	MAX_LIFETIME_MS = 700
	
	# C'tor
	def __init__(self, x, y, right, maker, power):
		# Call the parent c'tor
		super().__init__(x, y, "wall/laser.png", use_alpha=True)
		
		# Store other info
		self.direction_is_right = right
		self.maker = maker
		self.power = power
		self.lifetime = 0
	
	# Upodates the bullet, 
	def update(self, refresh_time, world, player, on_die, on_game_over):
		self.lifetime += refresh_time
		
		# If this bullet has lasted for more than {MAX_LIFETIME_MS}, kill it now
		if self.lifetime > Bullet.MAX_LIFETIME_MS:
			on_die()
			return
	
		if self.direction_is_right:
			self.rect.right += Bullet.HORIZ_MOV_INCR
		else:
			self.rect.right -= Bullet.HORIZ_MOV_INCR
		
		# Check if the bullet has hit the player
		if player.rect.colliderect(self.rect):
			on_die()
			if player.on_attacked(self.power):
				on_game_over()
			return
		
		# Check if the bullet is colliding with any of the map
		for o in world:
			# This is a fairly complex if statement, and I'm sorry for that :P
			# The purpose of this check is this, it checks that the object 
			# needs to be checked becuase bullet cannot pass through it, and 
			# in that case that the bullet has not collided with it. Finally,
			# it checks that the block also not the very weapon that fired the bullet
			if type(o) != self.maker and ((not self.direction_is_right and (o.dir == WallOpenDir.NONE or o.dir == WallOpenDir.LEFT_ONLY)) or (self.direction_is_right and (o.dir == WallOpenDir.NONE or o.dir == WallOpenDir.RIGHT_ONLY))) and self.rect.colliderect(o):
				on_die()
				return

class Player(pygame.sprite.Sprite):
	'''
		class for player and collision
		.map file: P
	'''
	# Constants
	HORIZ_MOV_INCR = 10
	
	# C'tor
	def __init__(self, x, y, initial_health):
		# Call the parent c'tor
		super().__init__()

		# Initialize the positional values
		self.movy = 0
		self.movx = 0
		self.x = x
		self.y = y

		# Initialize other locals
		self.contact = False
		self.jump = False

		# Store the names of all of the images
		self._images =  { 
			"run_left": "actions/run_left.png",
			"run_right": "actions/run_right.png",
			"idle_left": 'actions/idle_left.png',
			"idle_right": 'actions/idle_right.png',
			"jump_left": "actions/jump_left.png",
			"jump_right": "actions/jump_right.png",
			"down_left": "actions/down_left.png",
			"down_right": "actions/down_right.png"
		}

		# Get the initial image
		self.image = pygame.image.load(self._images["idle_right"]).convert_alpha()

		# Store information this sprite's size.
		self.rect = self.image.get_rect()
		self.rect.topleft = [x, y]

		# Store the intiial direction as right, and the move increment constant
		self.direction_is_right = True
		
		# Store the health
		self.health = initial_health
		self.initial_health = initial_health

	def on_attacked(self, ammount):
		self.health -= ammount
		return self.health <= 0
		
	def update(self, up, down, left, right, world):	
		if up:
			if self.contact:
				if self.direction_is_right:
					self.image = pygame.image.load(self._images["jump_right"]).convert_alpha()
				self.jump = True
				self.movy -= 20
		if down:
			if self.contact and self.direction_is_right:
				self.image = pygame.image.load(self._images["down_right"]).convert_alpha()
			if self.contact and not self.direction_is_right:
				self.image = pygame.image.load(self._images["down_left"]).convert_alpha()
		
		if not down and self.direction_is_right:
				self.image = pygame.image.load(self._images["idle_right"]).convert_alpha()
		
		if not down and not self.direction_is_right:
			self.image = pygame.image.load(self._images["idle_left"]).convert_alpha()
		
		if left:
			self.direction_is_right = False
			self.movx = -Player.HORIZ_MOV_INCR
			if self.contact:
				self.image = pygame.image.load(self._images["run_left"]).convert_alpha()
			else:
				self.image = self.image = pygame.image.load(self._images["jump_left"]).convert_alpha()
		
		if right:
			self.direction_is_right = True
			self.movx = Player.HORIZ_MOV_INCR
			if self.contact:
				self.image = pygame.image.load(self._images["run_right"]).convert_alpha()
			else:
				self.image = self.image = pygame.image.load(self._images["jump_right"]).convert_alpha()
		
		if not (left or right):
			self.movx = 0
		self.rect.right += self.movx
		
		self.collide(self.movx, 0, world)
		
		if not self.contact:
			self.movy += 0.3
			if self.movy > 10:
				self.movy = 10
			self.rect.top += self.movy
		
		if self.jump:
			self.movy += 2
			self.rect.top += self.movy
			if self.contact == True:
				self.jump = False
		
		self.contact = False
		self.collide(0, self.movy, world)

	def collide(self, movx, movy, world):
		self.contact = False
		
		# Check if the player is colliding with any of the map
		for o in world:
			if self.rect.colliderect(o):
				# Handle X overflow
				if movx > 0 and (o.dir == WallOpenDir.NONE or o.dir == WallOpenDir.LEFT_ONLY):
					self.rect.right = o.rect.left
				if movx < 0 and (o.dir == WallOpenDir.NONE or o.dir == WallOpenDir.RIGHT_ONLY):
					self.rect.left = o.rect.right
					
				# Handle Y overflow
				if movy > 0 and (o.dir == WallOpenDir.NONE or o.dir == WallOpenDir.UP_ONLY):
					self.rect.bottom = o.rect.top
					self.movy = 0
					self.contact = True
				if movy < 0 and (o.dir == WallOpenDir.NONE or o.dir == WallOpenDir.DOWN_ONLY):
					self.rect.top = o.rect.bottom
					self.movy = 0
					
	def has_won(self, win_blocks):
		for wb in win_blocks:
			if self.rect.colliderect(wb):
				return True
		
		return False

class Level(object):
	'''
		Read a map and create a level
		takes a .map file path and creates the appropriate sprites.
	'''
	
	# C'tor
	def __init__(self, level_file_name, player_health):
		# Initaialize instance variables
		self.world = []
		self.spawners = []
		self.win_blocks = []
		self.all_sprite = pygame.sprite.Group()
		self.object_size = 25
		self.player_health = player_health
		
		# Takes all of the lines from the level file and caches them
		with open(level_file_name, "r") as level_file:
			self.level_lines = level_file.readlines()
	
	# Intializes from level from the level file
	def init(self):
		x = 0
		y = 0
	
		# Reders the current level to the screen. 
		for row in self.level_lines:
			for col in row:
				# "X" is rendered a wall
				# "R", "L", "D" and "U" are rendered as "pass-through" walls
				if col == "X" or col == "R" or col == "L" or col == "D" or col == "U":
					wall = Wall(x, y, WallOpenDir.of(col))
					self.world.append(wall)
					self.all_sprite.add(wall)
				
				# "P" is rendered as the player (where there head begins)
				elif col == "P":
					self.player = Player(x, y, self.player_health)
					self.all_sprite.add(self.player)
					
				# "W" is a "win block", a block which completes the level upon touching
				elif col == "W":
					win_block = WinBlock(x, y)
					self.win_blocks.append(win_block)
					self.all_sprite.add(win_block)
					
				# numbers (0-9) are "Bad-Guy" blocks. They spawn bad guys, of relitive difficulty to the number.
				elif col.isdigit():
					my_spawner = Spawner(x, y, int(col))
					self.world.append(my_spawner)
					self.spawners.append(my_spawner)
					self.all_sprite.add(my_spawner)
				
				# Increment X counter
				x += self.object_size
				
			# Increment Y Counter
			y += self.object_size
			x = 0 # Reset X Counter
	
	# Resurs the size of the map as a tuple: (width, height)
	def get_size(self):
		lines = self.level_lines
		line = max(lines, key=len)
		width = (len(line)) * self.object_size
		height = (len(lines)) * self.object_size
		return (width, height)
