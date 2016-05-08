import pygame, colors
from rendering import *
from screen import Screen

class SplashScreen(Screen):
	"""
		Renderers the splash screen
	"""

	def __init__(self, surface, screen_size, on_click_func):
		"""Constructor
		"""
		
		super().__init__()
		
		# Create dependencies
		self.text_renderer = TextRenderer(colors.BLACK, 25, surface, pygame.font.SysFont("monospace", 15))
		self.shape_renderer = ShapeRenderer(surface)
		
		# Store settings
		self.screen_size = screen_size
		
		# Store the click handler
		self._on_click_func = on_click_func
		
	def handle_click(self):
		self._on_click_func()
	
	def render(self, refresh_time):
		"""Renderers the splash screen 
		"""
		# Set the backgroud to white
		self.shape_renderer.render_rect((0, 0 , self.screen_size[0], self.screen_size[1]), color=colors.WHITE)
		
		# Set up the text
		items = """Game Title: Take It Back,
Name: Jake Thurman,
CIS226-HYB1,
Summary: This game is a side scroller with the goal of
   reaching the end of each level while getting as many
   rings as possible, all without dying. There are be badies
   and weapons for the user to avoid, and other various
   obstacles. It will be a simple, fun game to waste time
   and give players a sense of accomplishment. 
   
You can select a level from the list that will appear on
   the next screen. Completed levels will turn Green, Failed
   levels will turn red and locked levels will be a darker gray.
 
To play the game, use the left and right arrow keys to move,
   and the up arrow or the space bar to jump.
   
CLICK ANYWHERE TO PLAY!""".split("\n")
		
		# Render the main text
		for i, item in enumerate(items):
			self.text_renderer.render(item, i + 1)
				
		screen_x, screen_y = self.screen_size
		
		# Draw a border arround the screen for decoration!
		self.shape_renderer.render_rect((0, 0, 10, screen_y), color=colors.BLUE)
		self.shape_renderer.render_rect((0, 0, screen_x, 10), color=colors.BLUE)
		self.shape_renderer.render_rect((screen_x - 10, 0, 10, screen_y), color=colors.BLUE)
		self.shape_renderer.render_rect((0, screen_y - 10, screen_x, 10), color=colors.BLUE)
		
		# Draw three circles at the bottom for fun
		self.shape_renderer.render_circle((screen_x - 100, screen_y - 50), 20, color=colors.GREEN)
		self.shape_renderer.render_circle((screen_x - 140, screen_y - 40), 20, color=colors.RED)
		self.shape_renderer.render_circle((screen_x - 200, screen_y - 60), 20, color=colors.GREEN)
