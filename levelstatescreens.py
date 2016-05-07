"""
	This file contains screens that exist to display state to the player
"""

import pygame, colors, resources
from rendering import *
from screen import Screen

class EndGameScreen(Screen):
	"""The game has ended here is what we say..."""

	def __init__(self, surface, screen_size, is_win, return_to_picker_screen_func, play_again_func):
		super().__init__()
		
		# Create Depndencies
		self.option_renderer = OptionRenderer(surface, pygame.font.SysFont("monospace", 30))
		self.shape_renderer = ShapeRenderer(surface)
		
		# Store settings and callbacks
		self.screen_size = screen_size
		self.is_win = is_win
		self.return_to_picker_screen_func = return_to_picker_screen_func
		self.play_again_func = play_again_func
		
		# Set the click handler
		self.set_on_click(self._click_handler)
		
	def _click_handler(self):
		# Do the requested action!
		if self.return_to_level.is_hovered:
			self.return_to_picker_screen_func()
		elif self.play_again.is_hovered:
			self.play_again_func()
	
	def render(self, refresh_time):
		# Set the backgroud color
		self.shape_renderer.render_rect((0, 0, self.screen_size[0], self.screen_size[1]), color=colors.DARK_GRAY, alpha=30)
		
		pygame.mouse.set_visible(True)	# Show the mouse on the levels screen
		
		# Take the correct message 
		message = resources.YOU_WON if self.is_win else resources.YOU_LOST
		
		# The position for the "you won/lost" message
		pos = (self.screen_size[0]/8, self.screen_size[1]/8)
		
		# Render the "you won/lost" message
		self.option_renderer.render(message, pos, color=colors.WHITE, hover_color=colors.WHITE)
		
		# Render the links at the bottom (pick a level and play again)
		self.return_to_level = self.option_renderer.render(resources.RETURN_TO_LEVEL_PICKER, (pos[0], self.screen_size[1]-pos[1]), color=colors.SILVER)
		self.play_again = self.option_renderer.render(resources.PLAY_AGAIN, (pos[0], self.screen_size[1]-(2*pos[1])), color=colors.SILVER)
