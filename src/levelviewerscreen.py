# Jacob Thurman
# Side Scroller Level Viewer Screen (Basically a read only version of levelscreen.LevelScreen)

from __future__ import division # Floating point division for python 2
import pygame, settingsmanager, colors, fonts, resources
from screen import Screen
from pygame.locals import K_ESCAPE, K_LEFT, K_RIGHT, K_UP, K_DOWN
from settingsmanager import Keys
from rendering import SpriteRenderer, ShapeRenderer, OptionRenderer

class MapViewerScreen(Screen):
	def __init__(self, data, level, camera_factory):
		""" C'tor for the screen.
		"""
		
		# Store injected dependencies
		self._screen_size = data.get_screen_size()
		self._screen_manager = data.get_screen_manager()
		self._level = level
		
		# Create and store custom dependencies
		self._eye = pygame.Rect(level.player.rect.x, level.player.rect.y, level.player.rect.w, level.player.rect.h)
		self._camera = camera_factory(self._eye)
		
		surface = data.get_surface()
		self._shape_renderer = ShapeRenderer(surface)
		self._sprite_renderer = SpriteRenderer(surface)
		self._option_renderer = OptionRenderer(surface, fonts.OPEN_SANS(size=30))
		
		# State
		self._up_move = 0
		self._left_move = 0
	
	# Handles pygame key change events
	def _handle_key_change(self, key, value):
		_MOVE_SPEED = 20 # Constant
		move_by = _MOVE_SPEED * (-1 if value else 1)
		
		if key == settingsmanager.get_user_setting(Keys.SETTING_JUMP_KEY):#or key == K_UP:
			self._up_move += move_by
		elif key == settingsmanager.get_user_setting(Keys.SETTING_CROUCH_KEY):#or key == K_DOWN:
			self._up_move -= move_by
		elif key == settingsmanager.get_user_setting(Keys.SETTING_LEFT_KEY):#or key == K_LEFT:
			self._left_move += move_by
		elif key == settingsmanager.get_user_setting(Keys.SETTING_RIGHT_KEY):#or key == K_RIGHT:
			self._left_move -= move_by
	
	# Handles key up events, and clears the stored value for any of the keys we were listening for
	def handle_key_up(self, key):
		self._handle_key_change(key, False)
		
		# if this is the escape key, quit the game
		if key == K_ESCAPE:
			self._return_to_level()
	
	# Handles key down events, and stores a flag for any of the keys we are listening for
	def handle_key_down(self, key):
		self._handle_key_change(key, True)
		
	def _return_to_level(self):
		self._screen_manager.go_back() # To Pause Screen
	
	def handle_click(self):
		"""Handles a click event
		"""
		# Exit explore
		if self._done_bttn.is_hovered:
			self._return_to_level()
			
		# Otherwise, center on the clicked position
		else: 
			x, y = pygame.mouse.get_pos()
			center = (self._screen_size[0] / 2, self._screen_size[1] / 2)
			offset = (x - center[0], y - center[1])
			
			self._eye.center = (self._eye.centerx + offset[0], self._eye.centery + offset[1])
		
	def render(self, refresh_time):
		"""Renders the map in a movable way
		"""

		pygame.mouse.set_visible(True) # Show the mouse inside the explore page
		
		# Set the backgroud to sky blue
		self._shape_renderer.render_rect((0, 0, self._screen_size[0], self._screen_size[1]), color=colors.SKY_BLUE)
	
		# Refresh the camera 
		self._eye.left += self._left_move
		self._eye.bottom += self._up_move
		self._camera.update() # Update the camera position
		
		# Get the sprites that we need to render
		visible_sprites, invisible_sprites = self._camera.get_all_that_can_see(self._level.all_sprite)
		
		# Handle rendering the visible sprites
		for s in visible_sprites:
			if s != self._level.player:
				# Render the sprite to the screen
				self._sprite_renderer.render(s, convert_rect=self._camera.convert_rect_for_render)
		
		done_pos = (self._screen_size[0] - (self._screen_size[0]/3), self._screen_size[1]-(self._screen_size[1]/8))
		self._done_bttn = self._option_renderer.render(resources.DONE_EXPLORING, done_pos, color=colors.SILVER)
		