import json
import fonts
import colors
import settingsmanager
import globals as g
from settingsmanager import Keys
from rendering import *
from screen import Screen
from icons import BackIcon
from pygame.locals import K_ESCAPE

def get_pack_data():
	with open(g.ROOT_PATH + "images/packs/packs.json") as packs:
		return json.load(packs)

class ImgSetPickerScreen(Screen):
	"""Allows the user to choose the image set setting
	"""
	
	def __init__(self, data):
		"""Constructor
		"""
		# Store given values
		self._screen_size = data.get_screen_size()
		self._screen_manager = data.get_screen_manager()
		
		# Create dependencies
		surface = data.get_surface()
		self.sprite_renderer = SpriteRenderer(surface)
		self.option_renderer = OptionRenderer(surface, fonts.OPEN_SANS(size=30))
		self.shape_renderer = ShapeRenderer(surface)
		
		self._packs_data = get_pack_data()
	
	def handle_click(self):
		if self.back_bttn.is_hovered():
			self._screen_manager.go_back()
			
		for text_rend, pack_key in self._options:
			if text_rend.is_hovered:
				# Update the user setting
				settingsmanager.update_user_setting(Keys.SETTING_IMG_SET, pack_key)
				
				# Return to the regular settings screen
				self._screen_manager.go_back()
		
	def handle_key_up(self, key):
		# Escape should mean return
		if key == K_ESCAPE:
			self._screen_manager.go_back()
	
	def render(self, refresh_time):
		ss = self._screen_size
			
		# Set the backgroud color
		self.shape_renderer.render_rect((0, 0, ss[0], ss[1]), color=colors.DARK_GRAY)
		
		# Render the back button
		self.back_bttn = self.sprite_renderer.render(BackIcon(ss[0] - ss[0]/8, ss[1]/8))
				
		# Reset the stored settings
		self._options = []
		
		i = 1
		for pack_key in sorted(self._packs_data.keys()):
			pack_title = self._packs_data[pack_key]
		
			# Draw a background for the example img
			self.shape_renderer.render_rect((28, (i * 80) - 44, 37, 67), color=colors.SILVER)

			# Draw the example img of the pack
			sprite = Sprite(30, (i * 80) - 40, g.ROOT_PATH + "images/packs/" + pack_key + "/idle_right.png", use_alpha=True)
			self.sprite_renderer.render(sprite)
			
			# Print the name of the pack
			text_rend = self.option_renderer.render(pack_title, (80, (i * 80) - 30), color=colors.SILVER)
			
			self._options.append((text_rend, pack_key))
						
			i += 1	
