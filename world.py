"""
	Defines Elements for the scroll game.
"""

import pygame, random
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
		
	_ALL_KEYS = ("X", "L", "R", "U", "D")
		
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
		
class HealthPack(Sprite):
	"""
		Class for "power up"/"health" blocks 
		.map file: +
	"""
	def __init__(self, x, y):
		# Init the parent class
		super().__init__(x, y, "wall/health_pack.png")
		
class Ring(Sprite):
	"""
		Class for "Bonus Star"/"Ring" blocks 
		.map file: *
	"""
	def __init__(self, x, y, grayscale=False):
		# Init the parent class
		super().__init__(x, y, "wall/ring.png", use_alpha=True, grayscale=grayscale)
		
class Weapon(Sprite):
	"""
		Class for weapon blacks 
		.map file 0-5
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
	
	def update(self, refresh_time, camera, player, obstacles, add_entity_func):
		# Increment the wait counter with the time since the last update
		self.last_fire_ticks += refresh_time
		
		# If we haven't waited long enough, we don't want to fire. Then, check 
		# a randomly generated integer in the range [0, 5 * (10 - power)]; if
		# that randomly returns 1, we want to fire
		should_fire = self.last_fire_ticks > self.min_fire_interval and random.randint(0, 5 * (10 - int(self.power/2))) == 1;
		
		# If the random number genderation says we should shoot, and we can see the player, shoot!
		if should_fire and camera.can_see(self):	
			is_right = player.rect.center[0] > self.rect.center[0]
			add_entity_func(Bullet(self.rect.right if is_right else self.rect.left, self.rect.center[1], is_right, self, self.power + 1))
			self.last_fire_ticks = 0 # Reset the wait counter
				
class Spawner(Sprite):
	"""
		Class for spawner blacks 
		.map file 6-9
	"""	
	SPAWN_PER_POWER_RATE = 0.3
	
	def __init__(self, x, y, power):
		# Init the parent class
		super().__init__(x, y, "wall/spawner.png", use_alpha=True)
		# Don't let users pass through these blocks
		self.dir = WallOpenDir.NONE
		# Store the power
		self.power = power
		# Store the fire interval
		self.min_fire_interval = 320 * (10 - power)
		# Say that we are halfway through our wait to fire initially.
		self.last_fire_ticks = (self.min_fire_interval / 2)
		# Create a list for our children so we don't create more than {power*SPAWN_PER_POWER_RATE at a time}
		self.spawn = []
		
	def _on_spawn_die(self, spawn):
		self.spawn.remove(spawn)
	
	def update(self, refresh_time, camera, player, obstacles, add_entity_func):	
		# Increment the wait counter with the time since the last update
		self.last_fire_ticks += refresh_time
		
		# If we haven't waited long enough, we don't want to fire, 
		# and there isn't too many spawn, check a randomly 
		# generated integer in the range [0, 60 * (10 - power)]; 
		# if that randomly returns 1, we want to fire
		should_fire = self.last_fire_ticks > self.min_fire_interval and len(self.spawn) < self.power*self.SPAWN_PER_POWER_RATE and random.randint(0, 60 * (10 - self.power)) == 1;
		
		# If the random number genderation says we should shoot, and we can see the player, shoot!
		if should_fire and camera.can_see(self):
			is_right = player.rect.center[0] > self.rect.center[0]
			x = self.rect.left if is_right else self.rect.left - self.rect.width
			y = self.rect.topleft[1] + random.randrange(-5, 5)
			
			my_spawn = Baddie(x, y, self, self.power + 1, self._on_spawn_die)
			add_entity_func(my_spawn)
			self.spawn.append(my_spawn)
			self.last_fire_ticks = 0 # Reset the wait counter
		

class Bullet(Sprite):	
	"""
		Faster than a speeding bullet...
		Wait... a moving bullet class.
		As shot by a "weapon" (0-5)
	"""
	# Constants
	HORIZ_MOV_INCR = 10
	MAX_LIFETIME_MS = 1000
	
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
	def update(self, refresh_time, camera, obstacles, player, on_die, on_game_over):
		self.lifetime += refresh_time
		
		# If this bullet has lasted for more than {MAX_LIFETIME_MS}, kill it now
		if self.lifetime > self.MAX_LIFETIME_MS:
			on_die()
			return
	
		if self.direction_is_right:
			self.rect.right += self.HORIZ_MOV_INCR
		else:
			self.rect.right -= self.HORIZ_MOV_INCR
		
		# Check if the bullet has hit the player
		if player.rect.colliderect(self.rect):
			on_die()
			player.reduce_health(self.power)
			if not player.is_alive():
				on_game_over()
			return
		
		# Check if the bullet is colliding with any of the map
		for o in obstacles:
			# This is a fairly complex if statement, and I'm sorry for that :P
			# The purpose of this check is this, it checks that the object 
			# needs to be checked becuase bullet cannot pass through it, and 
			# in that case that the bullet has not collided with it. Finally,
			# it checks that the block also not the very weapon that fired the bullet
			if type(o) != self.maker and ((not self.direction_is_right and (o.dir == WallOpenDir.NONE or o.dir == WallOpenDir.LEFT_ONLY)) or (self.direction_is_right and (o.dir == WallOpenDir.NONE or o.dir == WallOpenDir.RIGHT_ONLY))) and self.rect.colliderect(o):
				on_die()
				return
				
class Baddie(Sprite):
	"""
		This class represents a pathfinding enemie
		as spawned by a "spawner" block (6-10)		
	"""
	# Constants
	HORIZ_MOV_INCR = 2
	VERT_MOV_INCR = 8
	MAX_LIFETIME_MS = 20 * 1000
	ATTACK_POWER_RATIO = 0.1
		
	# C'tor
	def __init__(self, x, y, maker, power, before_death_func):		
		# Call the parent c'tor
		super().__init__(x, y, "actions/baddie_idle.png", use_alpha=True)
		
		# Initialize other locals
		self.maker = maker
		self.power = power
		self.lifetime = 0
		self.contact = False
		
		# Store callback
		self.before_death_func = before_death_func
		
	def update(self, refresh_time, camera, obstacles, player, on_die, on_game_over):
		# Increment the the lifetime counter
		self.lifetime += refresh_time
		
		# If this baddie has lasted for more than {MAX_LIFETIME_MS}, kill it now
		if self.lifetime > self.MAX_LIFETIME_MS:
			self.before_death_func(self)
			on_die()
			return
	
		# Handle the case that the baddie hits the player first
		if self.rect.colliderect(player.rect):
			player.reduce_health(self.power*self.ATTACK_POWER_RATIO) # Attack the player
			if not player.is_alive(): # Check if we killed the player
				on_game_over()
			return
		
		# Do not move if the player is not arround
		if not camera.can_see(self):
			return
		
		# Calculate the direction to move
		right = player.rect.center[0] > self.rect.center[0]
		left = player.rect.center[0] < self.rect.center[0]
		
		# Now, move the player by the {HORIZ_MOV_INCR} is the appropriate direction
		if right:
			movx = self.HORIZ_MOV_INCR 
		elif left:
			movx = -self.HORIZ_MOV_INCR
		else: 
			movx = 0
		
		self.rect.right += movx
		
		# Check if the baddie is colliding with any of the map
		# also check if we are standing on anything, otherwise we're falling.
		if left or right:
			for o in obstacles:
				# Check if we've running into this block. If so move back. (we can go through our maker)
				if o != self.maker and self.rect.colliderect(o):
					self.rect.right -= movx

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

	def reduce_health(self, ammount):
		self.health -= ammount
		
	def give_health(self, ammount):
		# If this will overflow our health, just set to full
		if self.health + ammount > self.initial_health:
			self.health = self.initial_health
		else: # Add as expected
			self.health += ammount
		
	def is_alive(self):
		return self.health > 0
		
	def update(self, up, down, left, right, obstacles):	
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
			self.movx = -self.HORIZ_MOV_INCR
			if self.contact:
				self.image = pygame.image.load(self._images["run_left"]).convert_alpha()
			else:
				self.image = self.image = pygame.image.load(self._images["jump_left"]).convert_alpha()
		
		if right:
			self.direction_is_right = True
			self.movx = self.HORIZ_MOV_INCR
			if self.contact:
				self.image = pygame.image.load(self._images["run_right"]).convert_alpha()
			else:
				self.image = self.image = pygame.image.load(self._images["jump_right"]).convert_alpha()
		
		if not (left or right):
			self.movx = 0
		self.rect.right += self.movx
		
		self._collide(self.movx, 0, obstacles)
		
		if not self.contact:
			self.movy += 0.3
			if self.movy > 10:
				self.movy = 10
			self.rect.top += self.movy
		
		if self.jump:
			self.movy += 2
			self.rect.top += self.movy
			if self.contact:
				self.jump = False
		
		self._collide(0, self.movy, obstacles)

	def _collide(self, movx, movy, obstacles):
		self.contact = False
		
		# Check if the player is colliding with any of the map
		for o in obstacles:
			if self.rect.colliderect(o):
				# Handle X overflow
				if movx > 0 and (o.dir == WallOpenDir.NONE or o.dir == WallOpenDir.LEFT_ONLY):
					self.rect.right = o.rect.left
				if movx < 0 and (o.dir == WallOpenDir.NONE or o.dir == WallOpenDir.RIGHT_ONLY):
					self.rect.left = o.rect.right
					
				# Handle Y overflow
				if movy > 0 and o.dir in (WallOpenDir.NONE, WallOpenDir.UP_ONLY):
					self.rect.bottom = o.rect.top
					self.movy = 0
					self.contact = True
				if movy < 0 and o.dir in (WallOpenDir.NONE, WallOpenDir.DOWN_ONLY):
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
	OBJECT_SIZE = 25
	
	# C'tor
	def __init__(self, level_file_name, init_player_health):
		# Initaialize instance variables
		self.obstacles = []
		self.attackers = []
		self.win_blocks = []
		self.bonus_stars = []
		self.health_packs = []
		self.all_sprite = pygame.sprite.Group()
		self.init_player_health = init_player_health
		self.stars = 0
		
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
				if col in WallOpenDir._ALL_KEYS:
					self._add(Wall(x, y, WallOpenDir.of(col)), self.obstacles)
				
				# "W" is a "win block", a block which completes the level upon touching
				elif col == "W":
					self._add(WinBlock(x, y), self.win_blocks)
				
				# "P" is rendered as the player (where there head begins)
				elif col == "P":
					self.player = Player(x, y, self.init_player_health)
					self.all_sprite.add(self.player)
				
				# numbers (0-9) are "Bad-Guy" blocks. They spawn bad guys, of relitive difficulty to the number.
				elif col.isdigit():
					my_spawner = Weapon(x, y, int(col)) if int(col) < 6 else Spawner(x, y, int(col))
					self._add(my_spawner, self.attackers, self.obstacles)
					
				elif col == "+":
					self._add(HealthPack(x, y), self.health_packs)
					
				elif col == "*":
					self._add(Ring(x, y), self.bonus_stars)
				
				# Increment X counter
				x += self.OBJECT_SIZE
							
			# Increment Y Counter
			y += self.OBJECT_SIZE
			x = 0 # Reset X Counter
		
		# Store the total number of rings/bonus stars in the level
		self.total_stars = len(self.bonus_stars)
	
	# Resurs the size of the map as a tuple: (width, height)
	def get_size(self):
		lines = self.level_lines
		line = max(lines, key=len)
		width = (len(line)) * self.OBJECT_SIZE
		height = (len(lines)) * self.OBJECT_SIZE
		return (width, height)
		
	"""
		private helper functions
	"""
	def _add(self, sprite, *lists):
		for list in lists:
			list.append(sprite)
		self.all_sprite.add(sprite)	
		
	def _remove(self, sprite, *lists):
		for list in lists:
			list.remove(sprite)
		self.all_sprite.remove(sprite)	
		
	def _increment_stars(self):
		self.stars += 1
		
	def _update(self, list, action):
		for item in list:
			if self.player.rect.colliderect(item): # If this item is being touched
				action() # Perform the custom action
				self._remove(item, list) # Remove the item from the world
	
	""" 
		World Update Methods 
		NOTE: Non-complete set of update functions.
	"""
	def update_health_packs(self):
		self._update(self.health_packs, lambda: self.player.give_health(self.init_player_health/5)) # Fill the player's health by 20%
	
	def update_bonus_stars(self):
		self._update(self.bonus_stars, self._increment_stars)
