import colors, resources, settingsmanager
from rendering import *
from screen import Screen
from pygame.locals import *

class BackIcon(Sprite):
	"""A simple back arrow icon.
	"""
	def __init__(self, x, y):
		super().__init__(x, y, "images/icons/back-arrow.png", use_alpha=True)

class SettingsScreen(Screen):
	"""Allows the user to choose settings such as the key mappings
	"""
	
	def __init__(self, surface, screen_size, screen_manager):
		"""Constructor
		"""
		# Store given values
		self.screen_size = screen_size
		self._screen_manager = screen_manager
		
		# Create dependencies
		self.sprite_renderer = SpriteRenderer(surface)
		self.option_renderer = OptionRenderer(surface, pygame.font.SysFont("monospace", 30))
		self.shape_renderer = ShapeRenderer(surface)
	
	def handle_click(self):
		if self.back_bttn.is_hovered():
			self._screen_manager.go_back()
	
	def render(self, refresh_time):
		# Set the backgroud color
		self.shape_renderer.render_rect((0, 0, self.screen_size[0], self.screen_size[1]), color=colors.DARK_GRAY)
		
		# Render the back button
		self.back_bttn = self.sprite_renderer.render(BackIcon(self.screen_size[0] - self.screen_size[0]/8, self.screen_size[1]/8))
				
		# Render the settings
		i = 1
		for key, title, value in settingsmanager.get_user_settings():
			self.option_renderer.render(title, (30, i * 40), color=colors.SILVER, hover_color=colors.SILVER)
			self.option_renderer.render(value, (250, i * 40))
			i += 1
