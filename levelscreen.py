# Jacob Thurman
# Jacob Thurman
# Side Scroller Game Screen

import pygame, sys, colors, json, resources
from rendering import *
from screen import Screen
from world import Level, Ring
from pygame.locals import *

class _settings:
	# Camera should move by thid number of pixels when it adjusts.
	# This nubmer should be low enough to dis-allow jerkiness when 
	# quickly moving up/down, but also low enough to avoid jerking
	# when the player jumps, and trying to rerender that each time
	CAMERA_ADJUST_PIXELS = 25 

class HealthBar:
	"""The side scroll game status bar"""
	# Constants
	HEIGHT = 15
	
	def __init__(self, surface, screen_size, player):
		self.shape_renderer = ShapeRenderer(surface)
		self.player = player
		self.screen_size = screen_size
	
	def _get_curr_color(self):
		# We want to draw the health bar as green normally, but
		# red if it is bellow one quarter of the initial health
		# level and yellow in bettween one quarer and two thrids
		
		if (self.player.initial_health / 4) >= self.player.health:
			return colors.RED
		elif (self.player.initial_health / 3) * 2 >= self.player.health:
			return colors.YELLOW
		else:
			return colors.GREEN
	
	def render(self):		
		# Pad the screen by one 8th of the total size (for the left, right and bottom)
		padding = (self.screen_size[0] / 8, self.screen_size[1] / 32)
		
		full_bar_size = (padding[0], self.screen_size[1] - (self.HEIGHT + padding[1]), self.screen_size[0] - (2 * padding[0]), self.HEIGHT)
		
		# Draw the full bar
		self.shape_renderer.render_rect(full_bar_size, color=colors.BLACK)
		
		# Draw the current health bar overtop
		self.shape_renderer.render_rect((full_bar_size[0], full_bar_size[1], full_bar_size[2] * (self.player.health/self.player.initial_health), full_bar_size[3]), color=self._get_curr_color())
		
class LevelRings:
	"""Rendering class for the rings display for a level"""
	def __init__(self, surface):
		self.sprite_renderer = SpriteRenderer(surface)
		
	def render(self, right, top, total_stars, stars):
		for i in range(total_stars):
			self.sprite_renderer.render(Ring(right - ((i + 1) * Level.OBJECT_SIZE), top, grayscale=(total_stars-i)>stars))

class LevelScreen(Screen):
	"""Handles rendering of the actual side scrolling game"""
	
	# Constructor
	# NOTE: This c'tor is not a legal Screen.ScreenManger factory
	def __init__(self, surface, screen_size, level_file, player_health, on_win_func, on_lose_func):	
		super().__init__()	
		
		# Store the passed in values (we don't surface as a global)
		self.screen_size = screen_size
		self._on_win_func = on_win_func
		self._on_lose_func = on_lose_func
		
		# Create dependencies
		self.shape_renderer = ShapeRenderer(surface)
		
		# Create a level object
		self.my_level = Level(level_file, player_health)
		self.my_level.init()
		
		# Create a camera object
		level_size = self.my_level.get_size()
		self.camera = Camera(surface, self.my_level.player.rect, level_size[0], level_size[1], _settings.CAMERA_ADJUST_PIXELS)
		
		# Create a overlay renderers
		self.health_bar = HealthBar(surface, screen_size, self.my_level.player)
		self.level_rings = LevelRings(surface)
		
		# Initialize key handling
		self.up = self.down = self.left = self.right = False
		
		# Create an array for all of the fired entities from attackers
		self.entities = []
	
	# Handles pygame key change events
	def _handle_key_change(self, key, value):
		if key == K_UP or key == K_SPACE:
			self.up = value
		elif key == K_DOWN:
			self.down = value
		elif key == K_LEFT:
			self.left = value
		elif key == K_RIGHT:
			self.right = value
	
	# Handles key up events, and clears the stored value for any of the keys we were listening for
	def handle_key_up(self, key):
		self._handle_key_change(key, False)
		
		# if this is the escaple key, quit the game
		if key == K_ESCAPE:
			self._on_lose_func() # TODO: Add a pause menu triggered here.
	
	# Handles key down events, and stores a flag for any of the keys we are listening for
	def handle_key_down(self, key):
		self._handle_key_change(key, True)
	
	def _add_entity(self, bullet):
		self.my_level.all_sprite.add(bullet)
		self.entities.append(bullet)
		
	def _on_entity_die(self, bullet):
		self.my_level.all_sprite.remove(bullet)
		self.entities.remove(bullet)
	
	# Renders a side scoller display
	def render(self, refresh_time):
		# Check if the player has one. If they have, 
		# call on_win_func() and return; we're done.
		if self.my_level.player.has_won(self.my_level.win_blocks):		
			self._on_win_func(self.my_level.total_stars, self.my_level.stars)
			return
		
		# Set the backgroud to sky blue
		self.shape_renderer.render_rect((0, 0, self.screen_size[0], self.screen_size[1]), color=colors.SKY_BLUE)
		
		pygame.mouse.set_visible(False)	# Hide the mouse inside the game
				
		# Update the player object based of the currently pressed keys	
		self.my_level.player.update(self.up, self.down, self.left, self.right, self.my_level.obstacles)
		
		# Handle updating spawners
		for attacker in self.my_level.attackers:
			attacker.update(refresh_time, self.camera, self.my_level.player, self.my_level.obstacles, self._add_entity)
			
		# Update any current enitities
		for entity in self.entities:
			entity.update(refresh_time, self.camera, self.my_level.obstacles, self.my_level.player, lambda: self._on_entity_die(entity), lambda: self._on_lose_func())
		
		# Update other items
		self.my_level.update_health_packs()
		self.my_level.update_bonus_stars()
		
		# Update the camera position
		self.camera.update()
		
		# Render all of the level's sprites
		self.camera.draw_sprites(self.my_level.all_sprite)
		
		# Render the status bar - if there is any reason to show it
		if len(self.my_level.attackers) != 0:
			self.health_bar.render()
			
		if self.my_level.total_stars != 0:
			self.level_rings.render(self.screen_size[0] - self.screen_size[0]/64, self.screen_size[1]/64, self.my_level.total_stars, self.my_level.stars)
		
		# Update the pygame display
		pygame.display.flip()
