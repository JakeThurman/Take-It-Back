import pygame, colors
from rendering import *
from screen import Screen

class LaunchScreen(Screen):
	"""Renderers the splash screen
	"""

	def __init__(self, surface, screen_size, start_game_func):
		"""Constructor
		"""
		
		super().__init__()
		
		# Create dependencies
		self.text_renderer = TextRenderer(colors.WHITE, 25, surface, pygame.font.SysFont("monospace", 15))
		self.shape_renderer = ShapeRenderer(surface)
		
		# Store settings
		self.screen_size = screen_size
		
		# Store the click handler
		self._start_game_func = start_game_func
		
	def handle_click(self):
		"""Handles a click event by begining the game
		"""
		self._start_game_func()
		
	def handle_key_up(self, key):
		"""Handles a key up event by begining the game
		"""
		self._start_game_func()
	
	def render(self, refresh_time):
		"""Renderers the splash screen 
		"""
		# Set the backgroud to white
		self.shape_renderer.render_rect((0, 0 , self.screen_size[0], self.screen_size[1]), color=colors.DARK_GRAY)
		
		# Set up the text
		items = """To play the game, use the left and right arrow keys to move,
and the up arrow or the space bar to jump.
   
   
   
CLICK ANYWHERE TO PLAY!""".split("\n")
		
		# Render the main text
		for i, item in enumerate(items):
			self.text_renderer.render(item, i + 1)
