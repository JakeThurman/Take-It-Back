import pygame, sys, colors
from pygame.locals import *
from rendering import *
from screen import Screen

class Logo(Sprite):
	def __init__(self, x, y):
		super().__init__(x, y, "images/logo.png", use_alpha=True)

class LaunchScreen(Screen):
	"""Renderers the splash screen
	"""

	def __init__(self, surface, screen_size, start_game_func):
		"""Constructor
		"""
		# init parent class
		super().__init__()
		
		# Create dependencies
		self.shape_renderer = ShapeRenderer(surface)
		self.sprite_renderer = SpriteRenderer(surface)
		self.option_renderer = OptionRenderer(surface, pygame.font.SysFont("monospace", 25))
		
		# Store settings
		self.screen_size = screen_size
		
		# Store the click handler
		self._start_game_func = start_game_func
		
	def handle_click(self):
		"""Handles a click event by begining the game
		"""
		self._start_game_func()
		
	def handle_key_up(self, key):
		# Close the game if escape is pressed
		if key == K_ESCAPE:
			pygame.quit()
			sys.exit()
	
		"""Handles a key up event by begining the game
		"""
		self._start_game_func()
		
	def _get_pos(self, n):
		"""Gets the position for a link positioned {n + 1} from the bottom of the screen.
		"""
		return ((self.screen_size[0]/8), self.screen_size[1]-((n + 1) * (self.screen_size[1]/8)))
	
	def render(self, refresh_time):
		"""Renderers the splash screen 
		"""
		# Set the backgroud to white
		self.shape_renderer.render_rect((0, 0 , self.screen_size[0], self.screen_size[1]), color=colors.DARK_GRAY)
			
		# Draw a logo image at the top-center of the screen
		self.sprite_renderer.render(Logo(self.screen_size[0]/2 - 100, self.screen_size[1]/4))
		
		# Render a set of options_renderer
		for i, text in enumerate(["Exit", "Settings", "Choose a Level"]):
			self.option_renderer.render(text, self._get_pos(i), color=colors.SILVER)
