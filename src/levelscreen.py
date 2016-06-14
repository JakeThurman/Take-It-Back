# Jacob Thurman
# Jacob Thurman
# Side Scroller Game Screen

from __future__ import division # Floating point division for python 2
import pygame, sys, colors, json, resources, settingsmanager
from rendering import *
from screen import Screen
from world import Level, Ring
from settingsmanager import Keys
from levelstatescreens import PauseMenuScreen
from pygame.locals import *

class _settings:
	# Camera should move by thid number of pixels when it adjusts.
	# This nubmer should be low enough to dis-allow jerkiness when 
	# quickly moving up/down, but also low enough to avoid jerking
	# when the player jumps, and trying to rerender that each time
	CAMERA_ADJUST_PIXELS = 25 

class HealthBar:
	"""The side scroll game status bar
	"""
	# Constants
	HEIGHT = 15
	
	def __init__(self, shape_renderer, screen_size, player):
		self.shape_renderer = shape_renderer
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
	"""Rendering class for the rings display for a level
	"""
	def __init__(self, sprite_renderer):
		self.sprite_renderer = sprite_renderer
		
	def render(self, right, top, total_stars, stars):
		for i in range(total_stars):
			self.sprite_renderer.render(Ring(right - ((i + 1) * Level.OBJECT_SIZE), top, grayscale=(total_stars-i)>stars))

class LevelScreen(Screen):
	"""Handles rendering of the actual side scrolling game
	"""
	
	# Constructor
	# NOTE: This c'tor is not a legal Screen.ScreenManger factory
	def __init__(self, surface, screen_size, screen_manager, level_title, level_file, player_health, win_func, lose_func, return_to_picker_func, restart_me_func):	
		super(LevelScreen, self).__init__()	
		
		# Store the passed in values (we don't surface as a global)
		self.screen_size = screen_size
		self.level_title = level_title
		self._on_win_func = win_func
		self._on_lose_func = lose_func
		self._screen_manager = screen_manager
		self._return_to_picker_func = return_to_picker_func
		self._restart_me_func = restart_me_func
				
		# Create a level object
		self.my_level = Level(level_file, player_health)
		self.my_level.init()
		
		# Create a camera object
		level_size = self.my_level.get_size()
		self.camera = Camera(surface, self.my_level.player.rect, level_size[0], level_size[1], _settings.CAMERA_ADJUST_PIXELS)
		
		# Create dependencies and overlay renderers
		self.sprite_renderer = SpriteRenderer(surface)
		self.shape_renderer = ShapeRenderer(surface)
		self.health_bar = HealthBar(self.shape_renderer, screen_size, self.my_level.player)
		self.level_rings = LevelRings(self.sprite_renderer)
		
		# Initialize key handling
		self.up = self.down = self.left = self.right = False
		
		# Create an array for all of the fired entities from attackers
		self.entities = []
	
	# Handles pygame key change events
	def _handle_key_change(self, key, value):
		if key == settingsmanager.get_user_setting(Keys.SETTING_JUMP_KEY):
			self.up = value
		elif key == settingsmanager.get_user_setting(Keys.SETTING_CROUCH_KEY):
			self.down = value
		elif key == settingsmanager.get_user_setting(Keys.SETTING_LEFT_KEY):
			self.left = value
		elif key == settingsmanager.get_user_setting(Keys.SETTING_RIGHT_KEY):
			self.right = value
	
	# Handles key up events, and clears the stored value for any of the keys we were listening for
	def handle_key_up(self, key):
		self._handle_key_change(key, False)
		
		# if this is the escaple key, quit the game
		if key == K_ESCAPE:
			self._pause_game()
	
	# Handles key down events, and stores a flag for any of the keys we are listening for
	def handle_key_down(self, key):
		self._handle_key_change(key, True)
	
	def _pause_game(self):
		self._screen_manager.set(lambda surface, screen_size, screen_manager: PauseMenuScreen(surface, screen_size, screen_manager, self.level_title, self._return_to_picker_func, self._restart_me_func))
	
	def _add_entity(self, bullet):
		self.my_level.all_sprite.add(bullet)
		self.entities.append(bullet)
		
	def _on_entity_die(self, ent):
		self.my_level.all_sprite.remove(ent)
		self.entities.remove(ent)
	
	# Renders a side scoller display
	def render(self, refresh_time):
		# Check if the player has one. If they have, 
		# call on_win_func() and return; we're done.
		if self.my_level.player.has_won(self.my_level.win_blocks):		
			self._on_win_func(self.my_level.total_stars, self.my_level.stars, self.my_level.player.health)
			return
		
		# Set the backgroud to sky blue
		self.shape_renderer.render_rect((0, 0, self.screen_size[0], self.screen_size[1]), color=colors.SKY_BLUE)
		
		pygame.mouse.set_visible(False)	# Hide the mouse inside the game
		
		# Update the player object based of the currently pressed keys	
		self.my_level.player.update(self.up, self.down, self.left, self.right, self.my_level.obstacles)
				
		# Refresh the camera 
		self.camera.update() # Update the camera position
		
		# Find the visible sprites
		visible_sprites, invisible_sprites = self.camera.get_all_that_can_see(self.my_level.all_sprite)
		visible_obstacles = [o for o in self.my_level.obstacles if o in visible_sprites]
		
		# Handle updating a spawner
		for s in self.my_level.attackers:
			s.add_time(refresh_time)
			if s in visible_sprites:
				s.try_attack(self.my_level.player, visible_obstacles, self._add_entity)
		
		# Handle updating a current enitity
		for s in self.entities:
			s.add_time(refresh_time)
			if s in visible_sprites:
				s.update(self.entities, visible_obstacles, self.my_level.player, lambda: self._on_entity_die(s), lambda: self._on_lose_func())
		
		# Handle rendering the visible sprites
		for s in visible_sprites:
			# Render the sprite to the screen
			self.sprite_renderer.render(s, convert_rect=self.camera.convert_rect_for_render)
		
		# Update other items
		self.my_level.update_health_packs()
		self.my_level.update_bonus_stars()
		
		# Render the health bar - if there is any reason to show it
		if len(self.my_level.attackers) != 0:
			self.health_bar.render()
		
		# If there are any rings (named stars TODO rename) render the ring count at the top
		if self.my_level.total_stars != 0:
			self.level_rings.render(self.screen_size[0] - self.screen_size[0]/64, self.screen_size[1]/64, self.my_level.total_stars, self.my_level.stars)
				
		# Update the pygame display
		pygame.display.flip()
