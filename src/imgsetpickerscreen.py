import json
import fonts
import colors
import settingsmanager
import resources
import globals as g
from settingsmanager import Keys
from rendering import *
from screen import Screen
from icons import BackIcon
from pygame.locals import K_ESCAPE
from paging import PagingHandler

def get_pack_data():
	with open(g.ROOT_PATH + "images/packs/packs.json") as packs:
		return json.load(packs)

class ImgSetPickerScreen(Screen):
	"""Allows the user to choose the image set setting
	"""
	LINE_HEIGHT = 80
	TEXT_SIZE = 30
	
	def __init__(self, data, page=0):
		"""Constructor
		"""
		# Store given values
		self._screen_size = data.get_screen_size()
		self._screen_manager = data.get_screen_manager()
		
		# Store data state
		self._page = page
		self._packs_data = get_pack_data()
		
		# Create dependencies
		surface = data.get_surface()
		self.sprite_renderer = SpriteRenderer(surface)
		self.option_renderer = OptionRenderer(surface, fonts.OPEN_SANS(size=self.TEXT_SIZE))
		self.shape_renderer = ShapeRenderer(surface)
		self._paging_handler = PagingHandler(data.get_screen_size, self.LINE_HEIGHT)
		
		# Initial state
		self._next_bttn = None
		
	
	def handle_click(self):
		if self._back_bttn.is_hovered():
			self._screen_manager.go_back()
			
		if self._next_bttn != None and self._next_bttn.is_hovered:
			self._screen_manager.set(lambda *args: ImgSetPickerScreen(*args, page=self._page+1))
			
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
	
	def _get_items(self):
		return self._paging_handler.filter_items(sorted(self._packs_data.keys()), self._page)
	
	def _is_last_page(self):
		return self._paging_handler.is_last_page(sorted(self._packs_data.keys()), self._page)
	
	def render(self, refresh_time):
		ss = self._screen_size
			
		# Set the backgroud color
		self.shape_renderer.render_rect((0, 0, ss[0], ss[1]), color=colors.DARK_GRAY)
		
		# Render the back button
		self._back_bttn = self.sprite_renderer.render(BackIcon(ss[0] - ss[0]/8, ss[1]/8))
		
		# Render the next page button if needed
		if not self._is_last_page():	
			next_link_pos = (ss[0] - self.TEXT_SIZE * 4, ss[1] - self.TEXT_SIZE * 2)
			self._next_bttn = self.option_renderer.render(resources.NEXT_PAGE, next_link_pos, color=colors.LIGHT_GRAY, hover_color=colors.SILVER)
		
		# Reset the stored settings
		self._options = []
		
		for i, pack_key in enumerate(self._get_items()):
			pack_title = self._packs_data[pack_key]
		
			# Draw a background for the example img
			self.shape_renderer.render_rect((28, (i * self.LINE_HEIGHT) + 36, 37, 67), color=colors.SILVER)

			# Draw the example img of the pack
			sprite = Sprite(30, (i * self.LINE_HEIGHT) + 40, g.ROOT_PATH + "images/packs/" + pack_key + "/idle_right.png", use_alpha=True)
			self.sprite_renderer.render(sprite)
			
			# Print the name of the pack
			text_rend = self.option_renderer.render(pack_title, (80, (i * self.LINE_HEIGHT) + 50), color=colors.SILVER)
			
			self._options.append((text_rend, pack_key))
