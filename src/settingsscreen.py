"""Manages the screen used for viewing/editing user settings
"""
from __future__ import division # Floating point division for python 2
import colors, resources, settingsmanager, fonts, textwrapping
from settingsmanager import Keys
from rendering import *
from screen import Screen
from pygame.locals import *
from icons import BackIcon
from imgsetpickerscreen import ImgSetPickerScreen, get_pack_data

VALUE_X_OFFSET = 315

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
		self._font_size = 30
		self._font = fonts.OPEN_SANS(size=self._font_size)
		self.option_renderer = OptionRenderer(surface, self._font)
		self.shape_renderer = ShapeRenderer(surface)
		
		self.edit_key = None
		
		self._pack_data = get_pack_data()
	
	def handle_click(self):
		if self.back_bttn.is_hovered():
			self._screen_manager.go_back()
			
		if self.edit_key == None and self.img_pack_bttn.is_hovered:
			self._screen_manager.set(ImgSetPickerScreen);
			
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
		for key, title, value in settingsmanager.get_key_settings():
			self.option_renderer.render(title, (40, i * 40), color=colors.SILVER, hover_color=colors.SILVER)
			rend = self.option_renderer.render(pygame.key.name(value).title(), (VALUE_X_OFFSET, i * 40))
			i += 1
			
			# Store the rendered setting object again
			self.settings.append((rend, key, title))
		
		# Render special settings
		self.option_renderer.render(resources.IMAGE_PACK, (40, i * 40), color=colors.SILVER, hover_color=colors.SILVER)
			
		
		pack_title = self._pack_data[settingsmanager.get_user_setting(Keys.SETTING_IMG_SET)]
		self.img_pack_bttn = self.option_renderer.render(pack_title, (VALUE_X_OFFSET, i * 40))
		# If we are in edit mode we need to render the overlay		
		if self.edit_key != None:		
			self.shape_renderer.render_rect((ss[0] / 6, ss[1] / 6, ss[0] - ss[0] / 3, ss[1] - ss[1] / 3), color=colors.WHITE)
			
			edit_text = textwrapping.wrapline(resources.PRESS_TO_CHANGE_KEY.format(self.edit_key[2]), self._font, ss[0] - ss[0] / 2)
			for i, line in enumerate(edit_text):
				self.option_renderer.render(line, (ss[0] / 4, ss[1] / 3 + (i - 1) * (self._font_size * 1.5)), color=colors.BLACK, hover_color=colors.BLACK)