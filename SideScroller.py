import pygame

class Camera(object):
	'''Class for center screen on the player'''
	def __init__(self, surface, player, level_width, level_height, pixes_to_adjust_by):
		self.player = player
		self.surface = surface
		self.rect = surface.get_rect()
		self.rect.center = self.player.center
		self.world_rect = pygame.Rect(0, 0, level_width, level_height)
		self.pixes_to_adjust_by = pixes_to_adjust_by

	def update(self):
		if self.player.centerx > self.rect.centerx + self.pixes_to_adjust_by:
			self.rect.centerx = self.player.centerx - self.pixes_to_adjust_by
		if self.player.centerx < self.rect.centerx - self.pixes_to_adjust_by:
			self.rect.centerx = self.player.centerx + self.pixes_to_adjust_by
		if self.player.centery > self.rect.centery + self.pixes_to_adjust_by:
			self.rect.centery = self.player.centery - self.pixes_to_adjust_by
		if self.player.centery < self.rect.centery - self.pixes_to_adjust_by:
			self.rect.centery = self.player.centery + self.pixes_to_adjust_by
			self.rect.clamp_ip(self.world_rect)

	def rel_rect(self, actor, camera):
		return pygame.Rect(actor.rect.x-camera.rect.x, actor.rect.y-camera.rect.y, actor.rect.w, actor.rect.h)

	def draw_sprites(self, sprites):
		for s in sprites:
			if s.rect.colliderect(self.rect):
				self.surface.blit(s.image, self.rel_rect(s, self))

class WallOpenDir:
	NONE = 0
	LEFT_ONLY = 1
	RIGHT_ONLY = 2
	UP_ONLY = 3
	DOWN_ONLY = 4
	
	# Gets a file image from a wall direction
	def get_file_name(dir):
		# We start with a map object...
		switcher = {
			1: "wall/left_only.png",
			2: "wall/right_only.png",
			3: "wall/up_only.png",
			4: "wall/down_only.png",
		}
		# Then return the needed value or this default value if none match.
		return switcher.get(dir, "wall/wall.png")
		
	# Returns a WallOpenDir value from a letter key
	def of(letter):
		# We start with a map object...
		switcher = {
			"R": WallOpenDir.RIGHT_ONLY,
			"L": WallOpenDir.LEFT_ONLY,
			"D": WallOpenDir.DOWN_ONLY,
			"U": WallOpenDir.UP_ONLY
		}
		# Then return the needed value or this default value if none match.
		return switcher.get(letter, WallOpenDir.NONE);
				
class Wall(pygame.sprite.Sprite):
	'''Class for wall blocks'''
	def __init__(self, x, y, dir):
		# Store positional information
		self.x = x
		self.y = y
		self.dir = dir

		# Init the parent class
		super().__init__()
		# Get the needed image
		self.image = pygame.image.load(WallOpenDir.get_file_name(dir)).convert()

		# Store size info about the sprite
		self.rect = self.image.get_rect()
		self.rect.topleft = [x, y]

class WinBlock(pygame.sprite.Sprite):
	"""Class for win blocks"""
	def __init__(self, x, y):
		# Store positional information
		self.x = x
		self.y = y
		
		# Init the parent class
		super().__init__()
		
		# Get the needed image
		self.image = pygame.image.load("wall/win_block.png").convert()

		# Store size info about the sprite
		self.rect = self.image.get_rect()
		self.rect.topleft = [x, y]

class Player(pygame.sprite.Sprite):
	'''class for player and collision'''
	def __init__(self, x, y):
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
		self.image = pygame.image.load(self._images.get("idle_right")).convert()

		# Store information this sprite's size.
		self.rect = self.image.get_rect()

		self.directionIsRight = True
		self.rect.topleft = [x, y]
		self.HORIZ_MOV_INCR = 10

	def update(self, up, down, left, right, world):
		if up:
			if self.contact:
				if self.directionIsRight:
					self.image = pygame.image.load(self._images.get("jump_right"))
				self.jump = True
				self.movy -= 20
		if down:
			if self.contact and self.directionIsRight:
				self.image = pygame.image.load(self._images.get("down_right")).convert_alpha()
			if self.contact and not self.directionIsRight:
				self.image = pygame.image.load(self._images.get("down_left")).convert_alpha()
		
		if not down and self.directionIsRight:
				self.image = pygame.image.load(self._images.get("idle_right")).convert_alpha()
		
		if not down and not self.directionIsRight:
			self.image = pygame.image.load(self._images.get("idle_left")).convert_alpha()
		
		if left:
			self.directionIsRight = False
			self.movx = -self.HORIZ_MOV_INCR
			if self.contact:
				self.image = pygame.image.load(self._images.get("run_left")).convert_alpha()
			else:
				self.image = self.image = pygame.image.load(self._images.get("jump_left")).convert_alpha()
		
		if right:
			self.directionIsRight = True
			self.movx = +self.HORIZ_MOV_INCR
			if self.contact:
				self.image = pygame.image.load(self._images.get("run_right")).convert_alpha()
			else:
				self.image = self.image = pygame.image.load(self._images.get("jump_right")).convert_alpha()
		
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
	'''Read a map and create a level'''
	
	# C'tor
	def __init__(self, level_file_name):
		# Initaialize instance variables
		self.world = []
		self.win_blocks = []
		self.all_sprite = pygame.sprite.Group()
		self.object_size = 25
		
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
					self.player = Player(x,y)
					self.all_sprite.add(self.player)
					
				elif col == "W":
					win_block = WinBlock(x, y)
					self.win_blocks.append(win_block)
					self.all_sprite.add(win_block)
				
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