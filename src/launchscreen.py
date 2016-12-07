"""Manages the screen shown at launch.
"""
from __future__ import division # Floating point division for python 2
import pygame, sys, colors, resources, fonts
import globals as g
from pygame.locals import *
from rendering import *
from screen import Screen
from settingsscreen import SettingsScreen

class Logo(Sprite):
	def __init__(self, x, y):
		super(Logo, self).__init__(x, y, g.ROOT_PATH + "images/logo.png", use_alpha=True)

class LaunchScreen(Screen):
	"""Renderers the splash screen
	"""

	def __init__(self, data, picker_screen_factory):
		"""Constructor
		"""
		# init parent class
		super(LaunchScreen, self).__init__()
		
		# Create dependencies
		surface = data.get_surface()
		self.shape_renderer = ShapeRenderer(surface)
		self.sprite_renderer = SpriteRenderer(surface)
		self.option_renderer = OptionRenderer(surface, fonts.OPEN_SANS())
		
		# Store settings
		self.screen_size = data.get_screen_size()
		self._screen_manager = data.get_screen_manager()
		self._picker_screen_factory = picker_screen_factory
		
	def handle_click(self):
		"""Handles a click event
		"""
		if self.choose_level_bttn.is_hovered:
			self._screen_manager.set(self._picker_screen_factory)
		elif self.settings_bttn.is_hovered:
			self._screen_manager.set(SettingsScreen)
		elif self.quit_bttn.is_hovered:
			pygame.quit()
			sys.exit()
		
	def handle_key_up(self, key):
		"""Handles a key up event by begining the game
		"""
		# Close the game if escape is pressed
		if key == K_ESCAPE:
			pygame.quit()
			sys.exit()
	
		
	def _get_pos(self, n):
		"""Gets the position for a link positioned {n} from the bottom of the screen.
		"""
		return ((self.screen_size[0]/8), self.screen_size[1]-(n * (self.screen_size[1]/8)))
	
	def render(self, refresh_time):
		"""Renderers the splash screen 
		"""
		# Set the backgroud to white
		self.shape_renderer.render_rect((0, 0 , self.screen_size[0], self.screen_size[1]), color=colors.DARK_GRAY)
			
		# Draw a logo image at the top-center of the screen
		self.sprite_renderer.render(Logo(self.screen_size[0]/2 - 100, self.screen_size[1]/4))
		
		# Render a set of options_renderer	
		self.choose_level_bttn = self.option_renderer.render(resources.CHOOSE_A_LEVEL, self._get_pos(3), color=colors.SILVER)
		self.settings_bttn     = self.option_renderer.render(resources.SETTINGS, self._get_pos(2), color=colors.SILVER)
		self.quit_bttn         = self.option_renderer.render(resources.QUIT_GAME, self._get_pos(1), color=colors.SILVER)
