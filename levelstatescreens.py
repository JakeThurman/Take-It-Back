"""This file contains screens that exist to display state to the player
"""

import pygame, sys, colors, resources
from rendering import *
from screen import Screen
from settingsscreen import SettingsScreen
from pygame.locals import K_ESCAPE

class EndGameScreen(Screen):
	"""The game has ended here is what we say...
	"""
	
	def __init__(self, surface, screen_size, screen_manager, is_win, play_again_func, completion_percentage=None):
		"""Constructor
		"""
	
		super().__init__()
		
		# Create Depndencies
		self.option_renderer = OptionRenderer(surface, pygame.font.SysFont("monospace", 30))
		self.shape_renderer = ShapeRenderer(surface)
		
		# Store settings and callbacks
		self.screen_size = screen_size
		self._screen_manager = screen_manager
		self.is_win = is_win # TODO: move special win handling out to GameWonScreen and GameLostScreen
		self.completion_percentage = completion_percentage
		self.play_again_func = play_again_func
				
	def _go_to_level_picker(self):
		# We need to go back twice here, once back to the level, again back to the picker
		self._screen_manager.go_back()
		self._screen_manager.go_back()
	
	def handle_key_up(self, key):
		"""When the user presses the ESC key, assume they wan to 
		"""
		if key == K_ESCAPE:
			self._go_to_level_picker()
	
	def handle_click(self):
		"""Handles a click event
		"""
		if self.return_to_level.is_hovered:
			self._go_to_level_picker()
		elif self.play_again.is_hovered:
			self.play_again_func()
		elif self.quit_button.is_hovered:
			pygame.quit()
			sys.exit()
	
	def render(self, refresh_time):
		"""Renders the end game screen
		"""
	
		# Set the backgroud color
		self.shape_renderer.render_rect((0, 0, self.screen_size[0], self.screen_size[1]), color=colors.DARK_GRAY, alpha=30)
		
		# Show the mouse on the end game screen
		pygame.mouse.set_visible(True)
		
		# Take the correct message 
		message = resources.YOU_WON if self.is_win else resources.YOU_LOST
		
		# The position for the "you won/lost" message
		pos = (self.screen_size[0]/8, self.screen_size[1]/8)
		
		# Render the "you won/lost" message
		self.option_renderer.render(message, pos, color=colors.WHITE, hover_color=colors.WHITE)
		
		# For a win screen add the completion percentage line
		if self.is_win:
			self.option_renderer.render(resources.COMPLETION_PERCENTAGE.format(str(self.completion_percentage)), (pos[0], pos[1]*2), color=colors.LIGHT_GRAY, hover_color=colors.LIGHT_GRAY)
		
		# Render the links at the bottom (pick a level and play again)
		self.return_to_level = self.option_renderer.render(resources.CHOOSE_A_LEVEL, (pos[0], self.screen_size[1]-(3*pos[1])), color=colors.SILVER)
		self.play_again      = self.option_renderer.render(resources.PLAY_AGAIN, (pos[0], self.screen_size[1]-(2*pos[1])), color=colors.SILVER)
		self.quit_button     = self.option_renderer.render(resources.QUIT_GAME, (pos[0], self.screen_size[1]-pos[1]), color=colors.SILVER)
		
	
class GameWonScreen(EndGameScreen):
	"""Win specific overload of the EndGameScreen
	"""
	def __init__(self, surface, screen_size, screen_manager, play_again_func, completion_percentage):
		super().__init__(surface, screen_size, screen_manager, True, play_again_func, completion_percentage=completion_percentage)
	
class GameLostScreen(EndGameScreen):
	"""Loss specific overload of the EndGameScreen
	"""
	def __init__(self, surface, screen_size, screen_manager, play_again_func):
		super().__init__(surface, screen_size, screen_manager, False, play_again_func)

class PauseMenuScreen(Screen):
	"""A level is paused. Give the user the option to quit, restart etc.
	"""

	def __init__(self, surface, screen_size, screen_manager, level_name, return_to_picker_screen_func, restart_func):
		"""Constructor
		"""
		super().__init__()
		
		# Create Depndencies
		self.option_renderer = OptionRenderer(surface, pygame.font.SysFont("monospace", 30))
		self.shape_renderer = ShapeRenderer(surface)
		
		# Store settings and callbacks
		self.screen_size = screen_size
		self._screen_manager = screen_manager
		self.level_name = level_name
		self.return_to_picker_screen_func = return_to_picker_screen_func
		self.restart_func = restart_func
		
		# Locals
		self._went_to_settings = False
	
	def handle_click(self):
		"""Handles a click event
		"""
		if self.return_to_level.is_hovered:
			self.return_to_picker_screen_func()
		elif self.restart.is_hovered:
			self._screen_manager.go_back()
			self._screen_manager.go_back()
			self.restart_func()
		elif self.quit_button.is_hovered:
			pygame.quit()
			sys.exit()
		elif self.continue_bttn.is_hovered:
			self._screen_manager.go_back()
		elif self.settings_bttn.is_hovered:
			self._screen_manager.set(SettingsScreen)
			self._went_to_settings = True
	
	def handle_key_up(self, key):
		"""When the user presses the ESC key, we want to go back to the game.
		"""
		if key == K_ESCAPE:
			self._screen_manager.go_back()			
	
	def _get_pos(self, n):
		"""Returns a position tuple for a option line n about the bottom of the screen
		"""
		return (self.screen_size[0]/8, self.screen_size[1]-(n*self.screen_size[1]/8))
	
	def render(self, refresh_time):
		"""Renders the pause screen
		"""
	
		# Set the backgroud color
		alpha = None if self._went_to_settings else 30
		self.shape_renderer.render_rect((0, 0, self.screen_size[0], self.screen_size[1]), color=colors.MID_GRAY, alpha=alpha)
		
		# Show the mouse on the pause screen
		pygame.mouse.set_visible(True)	
				
		# The position for the "you won/lost" message
		pos = (self.screen_size[0]/8, self.screen_size[1]/8)
		
		# Render the "you won/lost" message
		self.option_renderer.render(resources.PAUSED_MESSAGE.format(self.level_name), pos, color=colors.WHITE, hover_color=colors.WHITE)
		
		# Render the links at the bottom (pick a level and play again)
		self.continue_bttn   = self.option_renderer.render(resources.CONTINUE_GAME, self._get_pos(5), color=colors.SILVER)
		self.restart         = self.option_renderer.render(resources.RESTART_LEVEL, self._get_pos(4), color=colors.SILVER)
		self.settings_bttn   = self.option_renderer.render(resources.SETTINGS, self._get_pos(3), color=colors.SILVER)
		self.return_to_level = self.option_renderer.render(resources.RETURN_TO_LEVEL_PICKER, self._get_pos(2), color=colors.SILVER)
		self.quit_button     = self.option_renderer.render(resources.QUIT_GAME, self._get_pos(1), color=colors.SILVER)
