"""
	This file includes the SideScrollLevelPickerScreen class 
	and all of the components it exclusivly requires

"""

import pygame, sys, colors, json, resources
from rendering import *
from screen import Screen
from pygame.locals import *
from levelstatescreens import EndGameScreen
from levelscreen import LevelScreen

class _consts:
	"""Constants needed by the game"""
	
	"""SETTINGS"""
	# The default player health when none is specifically specified
	DEFAULT_PLAYER_HEALTH = 20

	"""LEVEL FILES"""
	# The folder where levels are stored
	LEVELS_PREFIX = "levels/"
	# The path to the data file
	JSON_DATA_FILE_NAME = "levels/data.json"
	# The name of a package
	PACKAGE_JSON_FILE_NAME = "/package.json"

	"""JSON KEYS"""
	# data.json: The json key for completed items
	COMPLETED_LEVELS_KEY = "completed"
	# data.json: The total rings for a completed level
	COMPLETED_LEVEL_TOTAL_RINGS_KEY = "total-rings"
	# data.json: The rings found for a completed level
	COMPLETED_LEVEL_MY_RINGS_KEY = "rings"	
	# data.json: The json key for failed items
	FAILED_LEVELS_KEY = "failed"
	# data.json: The json key for all of the packages
	PACKAGES_KEY = "packages"
	# package.json: The name of this package
	PACKAGE_NAME_KEY = "name"
	# package.json: The levels in this package
	PACKAGE_LEVELS_KEY = "levels"
	# package.json: The name of this level
	LEVEL_NAME_KEY = "name"
	# package.json: The name of the map file
	LEVEL_MAP_FILE_KEY = "map"
	# package.json: The health to provide a player for this level
	LEVEL_PLAYER_HEALTH_KEY = "helath"


#                        \/       /
# Sprite classes for the /\ and \/ icons on the picker 
# screeen for failed and completed levels respectfully.
class FailedIcon(Sprite):
	def __init__(self, x, y):
		super().__init__(x, y, "icons/x-mark.png", use_alpha=True)

class CompletedIcon(Sprite):
	def __init__(self, x, y):
		super().__init__(x, y, "icons/check.png", use_alpha=True)
	
# Helper class, for getting named valus for level links (and header)
class LevelLine:
	def __init__(self, name, is_header = False, file_path=None, player_health=None):
		self.name = name
		self.is_header = is_header
		self.file_path = file_path
		self.el = None
		self.player_health = player_health
		
	def set_el(self, el):
		self.el = el
	
class LevelPickerScreen(Screen):
	"""Handles picking a side scroller game"""

	# Constructor
	# NOTE: This c'tor is not a legal Screen.ScreenManger factory
	def __init__(self, surface, screen_size, set_screen_func):		
		super().__init__()
	
		# Create rendering dependencies
		self.package_text_renderer = OptionRenderer(surface, pygame.font.Font(None, 40), do_hover=False)
		self.level_text_renderer = OptionRenderer(surface, pygame.font.SysFont("monospace", 25))
		self.shape_renderer = ShapeRenderer(surface)
		self.sprite_renderer = SpriteRenderer(surface)
		
		# Store passed in values as needed
		self._set_screen_func = set_screen_func
		self.screen_size = screen_size
		
		# Create links to all the levels we need
		# First, get all of the level packages we can use
		with open(_consts.JSON_DATA_FILE_NAME, "r") as data_file:    
			self.json_data = json.load(data_file)
			
		# Here are all the lines for the levels.
		# This includes levels and headers
		self.level_lines = []
		
		# Next, add each package
		for level_package_path in self.json_data[_consts.PACKAGES_KEY]:
			# Open the package.json file for this folder
			with open(_consts.LEVELS_PREFIX + level_package_path + _consts.PACKAGE_JSON_FILE_NAME) as level_package:
				# Load the package json
				level_package_data = json.load(level_package)
				
				# Create a line for the package header and a blank one for spacing
				self.level_lines.append(LevelLine("", is_header = True))
				self.level_lines.append(LevelLine(level_package_data[_consts.PACKAGE_NAME_KEY], is_header = True))
				
				# Now create a line for each actual level.
				for level_data in level_package_data[_consts.PACKAGE_LEVELS_KEY]:
					# Math to map file
					file_path = _consts.LEVELS_PREFIX + level_package_path + "/" + level_data[_consts.LEVEL_MAP_FILE_KEY]
					# Player health value for this level
					player_health = level_data.get(_consts.LEVEL_PLAYER_HEALTH_KEY, _consts.DEFAULT_PLAYER_HEALTH)
					# Add a line for the level name
					self.level_lines.append(LevelLine(level_data[_consts.LEVEL_NAME_KEY], file_path=file_path, player_health=player_health))
		
		# Call the click handler on click!
		self.set_on_click(self._click_handler)
	
	def _click_handler(self):			
		# Find the element that is at that position
		clicked = [ll for ll in self.level_lines if not ll.is_header and ll.el.is_hovered]
		
		# If the user didn't click on anything, don't do anything
		if len(clicked) != 1:
			return
			
		# Now, we only want to keep arround that single element
		clicked = clicked[0]
		
		self._play_level(clicked.file_path, clicked.player_health)
		
	def _play_level(self, file_path, player_health):
		def win(total_rings, my_rings):
			self._on_level_won(file_path, total_rings, my_rings, player_health)
		def lose():
			self._on_level_lost(file_path, player_health)
	
		# Now set the screen to the chosen level!
		self._set_screen_func(lambda surface, screen_size: LevelScreen(surface, screen_size, file_path, player_health, win, lose))
	
	def _go_to_me(self):
		# Set the screen to this object
		self._set_screen_func(lambda surface, screen_size: self)
		
	def _on_level_won(self, file_path, total_rings, my_rings, player_health):
		data_changed = False
		
		# Shortcut names
		failed = self.json_data[_consts.FAILED_LEVELS_KEY]
		completed = self.json_data[_consts.COMPLETED_LEVELS_KEY]
		
		# Add the file to the completed levels array
		if file_path not in completed or completed[file_path][_consts.COMPLETED_LEVEL_MY_RINGS_KEY] < my_rings:
			completed[file_path] = {}
			completed[file_path][_consts.COMPLETED_LEVEL_MY_RINGS_KEY] = my_rings
			completed[file_path][_consts.COMPLETED_LEVEL_TOTAL_RINGS_KEY] = total_rings
			data_changed = True
			
		# Remove it from the failed array
		if file_path in failed:
			failed.remove(file_path)
			data_changed = True
			
		# Update the data file if need be
		if data_changed:
			self._dump_data_file()
	
		# Show the end game screeen
		self._set_end_game_screen(True, file_path, player_health)
	
	def _on_level_lost(self, file_path, player_health):		
		# Shortcut names
		failed = self.json_data[_consts.FAILED_LEVELS_KEY]
		completed = self.json_data[_consts.COMPLETED_LEVELS_KEY]
	
		# Update the data that needs to be
		if not file_path in completed and not file_path in failed:
			failed.append(file_path)
			self._dump_data_file()
	
		# Show the end game screen
		self._set_end_game_screen(False, file_path, player_health)
		
	def _dump_data_file(self):
		# Update the data file with new data
		with open(_consts.JSON_DATA_FILE_NAME, 'w') as outfile:
			json.dump(self.json_data, outfile, indent=2)
	
	def _set_end_game_screen(self, is_win, file_path, player_health):
		# Set the screen to an EndGameScreen. We give this a callback to return to the picker screen, and a callback to replay to same level.
		self._set_screen_func(lambda surface, screen_size: EndGameScreen(surface, screen_size, is_win, self._go_to_me, lambda: self._play_level(file_path, player_health)))
		
	def render(self, refresh_time):
		# Set the backgroud color
		self.shape_renderer.render_rect((0, 0, self.screen_size[0], self.screen_size[1]), color=colors.DARK_GRAY)
		
		pygame.mouse.set_visible(True)	# Show the mouse on the levels screen
		
		# line-sizing constants
		INNER_LEFT = 30
		OUTER_LEFT = 65
		LINE_HEIGHT = 30
		
		# Render each line
		for i, line in enumerate(self.level_lines):
			el_pos = (INNER_LEFT if line.is_header else OUTER_LEFT, i * LINE_HEIGHT)
			
			# Render the line appropriately
			if line.is_header:
				el = self.package_text_renderer.render(line.name, el_pos, color=colors.WHITE)
			elif line.el != None and line.file_path in self.json_data[_consts.COMPLETED_LEVELS_KEY]:
				# Get the ring scroe for this level
				my_rings = self.json_data[_consts.COMPLETED_LEVELS_KEY][line.file_path][_consts.COMPLETED_LEVEL_MY_RINGS_KEY]
				total_rings = self.json_data[_consts.COMPLETED_LEVELS_KEY][line.file_path][_consts.COMPLETED_LEVEL_TOTAL_RINGS_KEY]
			
				# Create an object for the line including the rings.
				compltion_percentage = int((my_rings/total_rings)*100) if total_rings != 0 else 100
				line_text = line.name + " (" + str(compltion_percentage) + "%)"
			
				el = self.level_text_renderer.render(line_text, el_pos, color=colors.MID_GREEN, hover_color=colors.PALE_GREEN)
				self.sprite_renderer.render(CompletedIcon(INNER_LEFT, el_pos[1]))
			elif line.el != None and line.file_path in self.json_data[_consts.FAILED_LEVELS_KEY]:
				el = self.level_text_renderer.render(line.name, el_pos, color=colors.RED, hover_color=colors.TOMATO)
				self.sprite_renderer.render(FailedIcon(INNER_LEFT, el_pos[1]))
			else:
				el = self.level_text_renderer.render(line.name, el_pos, color=colors.SILVER)
			
			# Finally, store the rendered elemenet for click handling
			line.set_el(el)
