import pygame, colors
from rendering import *
from screen import Screen

# Renderers the splash screen
class SplashScreen(Screen):
	# Constructor
	def __init__(self, surface, screen_size):
		self.text_renderer = TextRenderer(colors.BLACK, 25, surface, pygame.font.SysFont("monospace", 15))
		self.shape_renderer = ShapeRenderer(surface)
		self.screen_size = screen_size
	
	# Renderers the splash screen 
	def render(self, refresh_time):
		# Set the backgroud to white
		self.shape_renderer.render_rect((0, 0 , self.screen_size[0], self.screen_size[1]), color=colors.WHITE)
		
		# Set up the text
		self.text_renderer.render('Game Title: Take It Back', 1)
		self.text_renderer.render('Name: Jake Thurman', 2)
		self.text_renderer.render('CIS226-HYB1', 3)
		self.text_renderer.render('Summary: This game will be a side scroller with', 5)
		self.text_renderer.render('the goal of taking some object to the end of each', 6)
		self.text_renderer.render('level. There will be badies for the user to avoid,', 7)
		self.text_renderer.render('and other various obstacles. It will be a simple,', 8)
		self.text_renderer.render('fun game to waste time and give players a sense', 9)
		self.text_renderer.render('of accomplishment.', 10)
		self.text_renderer.render('CLICK ANYWHERE TO PLAY!', 12)
		
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
