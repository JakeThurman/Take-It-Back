import colors, resources, settingsmanager
from rendering import *
from screen import Screen
from pygame.locals import *
from icons import BackIcon

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
		
		self.edit_key = None
	
	def handle_click(self):
		if self.back_bttn.is_hovered():
			self._screen_manager.go_back()
			
		for item in self.settings:
			if item[0].is_hovered:
				self.edit_key = item
			
	def handle_key_up(self, key):
		# Escape should mean return
		if key == K_ESCAPE:
			if self.edit_key == None:
				self._screen_manager.go_back()
			else:
				self.edit_key = None
		elif self.edit_key != None:
			settingsmanager.update_user_setting(self.edit_key[1], key)
			self.edit_key = None
	
	def render(self, refresh_time):
		ss = self.screen_size
			
		# Set the backgroud color
		self.shape_renderer.render_rect((0, 0, ss[0], ss[1]), color=colors.DARK_GRAY)
		
		# Render the back button
		self.back_bttn = self.sprite_renderer.render(BackIcon(ss[0] - ss[0]/8, ss[1]/8))
				
		# Reset the stored settings
		self.settings = []
				
		# Render the settings		
		i = 1
		for key, title, value in settingsmanager.get_user_settings():
			self.option_renderer.render(title, (40, i * 40), color=colors.SILVER, hover_color=colors.SILVER)
			rend = self.option_renderer.render(pygame.key.name(value).title(), (250, i * 40))
			i += 1
			
			# Store the rendered setting object again
			self.settings.append((rend, key, title))
			
		# If we are in edit mode we need to render the overlay		
		if self.edit_key != None:		
			self.shape_renderer.render_rect((ss[0] / 4, ss[1] / 4, ss[0] - ss[0] / 4, ss[1] - ss[1] / 4), color=colors.WHITE)
			
			edit_text = "Press a key to use as the {0} key.".format(self.edit_key[2]) #TODO: Localize me
			self.option_renderer.render(edit_text, (ss[0] / 4, ss[1] / 3), color=colors.BLACK, hover_color=colors.BLACK)
