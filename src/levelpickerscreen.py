"""
	This file includes the SideScrollLevelPickerScreen class 
	and all of the components it exclusivly requires

"""

from __future__ import division # Floating point division for python 2
import pygame, sys, colors, json, resources, settingsmanager, fonts
import globals as g
from rendering import *
from screen import Screen
from pygame.locals import K_ESCAPE
from settingsmanager import Keys
from levelstatescreens import GameWonScreen, GameLostScreen
from levelscreen import LevelScreen
from launchscreen import LaunchScreen
from icons import BackIcon

class Consts:
	"""Constant Settings
	"""
	# The default player health when none is specifically specified
	DEFAULT_PLAYER_HEALTH = 20

#                        \/       /
# Sprite classes for the /\ and \/ icons on the picker 
# screeen for failed and completed levels respectfully.
class FailedIcon(Sprite):
	def __init__(self, x, y):
		super(FailedIcon, self).__init__(x, y, g.ROOT_PATH + "images/icons/x-mark.png", use_alpha=True)

class CompletedIcon(Sprite):
	def __init__(self, x, y):
		super(CompletedIcon, self).__init__(x, y, g.ROOT_PATH + "images/icons/check.png", use_alpha=True)
		
# Sprite icon for locked levels.
class LockedIcon(Sprite):
	def __init__(self, x, y):
		super(LockedIcon, self).__init__(x, y, g.ROOT_PATH + "images/icons/locked.png", use_alpha=True)
	
# Helper class, for getting named valus for level links (and header)
class LevelLine:
	def __init__(self, name, is_header = False, file_path=None, player_health=None, locked=False, unlocks=[]):
		self.name = name
		self.is_header = is_header
		self.file_path = file_path
		self.el = None
		self.player_health = player_health
		self.locked = locked
		self.unlocks = unlocks
		
	def set_el(self, el):
		self.el = el
	

# line-sizing constants
INNER_LEFT = 30
OUTER_LEFT = 65
LINE_HEIGHT = 30
	
class LevelPickerScreen(Screen):
	"""Handles picking a side scroller game"""
	
	def __init__(self, surface, screen_size, screen_manager, page=0, _cached_level_lines=None):		
		"""Constructor
		"""
		super(LevelPickerScreen, self).__init__()
	
		# Create rendering dependencies
		self.package_text_renderer = OptionRenderer(surface, fonts.OPEN_SANS(size=31), do_hover=False)
		self.level_text_renderer = OptionRenderer(surface, fonts.OPEN_SANS(size=25))
		self.link_text_renderer = OptionRenderer(surface, fonts.OPEN_SANS())
		self.shape_renderer = ShapeRenderer(surface)
		self.sprite_renderer = SpriteRenderer(surface)
		
		# Store passed in values as needed
		self._screen_manager = screen_manager
		self.screen_size = screen_size
		self._page = page
		
		# Initialize the levels and there titles by scanning the data 
		# file and going in and loading all of the package members
		if _cached_level_lines == None:
			self.level_lines = settingsmanager.use_json(lambda json: self._load_packages(json[Keys.PACKAGES_KEY]))
		else:
			self.level_lines = _cached_level_lines	
	
	def _load_packages(self, packages):
		# Here are all the lines for the levels.
		# This includes levels and headers
		level_lines = []
	
		# Next, add each package
		for level_package_path in packages:
			# Open the package.json file for this folder
			with open(g.APP_DATA_PATH + Keys.LEVELS_PREFIX + level_package_path + Keys.PACKAGE_JSON_FILE_NAME) as level_package:
				# Load the package json
				level_package_data = json.load(level_package)
				
				level_lines.append(LevelLine(level_package_data[Keys.PACKAGE_NAME_KEY], is_header = True))
				
				# Now create a line for each actual level.
				for level_data in level_package_data[Keys.PACKAGE_LEVELS_KEY]:
					# Math to map file
					file_path = Keys.LEVELS_PREFIX + level_package_path + "/" + level_data[Keys.LEVEL_MAP_FILE_KEY]
					
					# Player health value for this level
					player_health = level_data.get(Keys.LEVEL_PLAYER_HEALTH_KEY, Consts.DEFAULT_PLAYER_HEALTH)
					
					# Is this level locked? (Not by default)
					locked = level_data.get(Keys.LEVEL_LOCKED_KEY, False)
					
					# Get the full path for the map files this level unlocks
					unlocks = []
					for map_file in level_data.get(Keys.LEVEL_UNLOCKS_KEY, []):
						unlocks.append(Keys.LEVELS_PREFIX + level_package_path + "/" + map_file)
					
					# Add a line for the level name
					level_lines.append(LevelLine(level_data[Keys.LEVEL_NAME_KEY], file_path=file_path, player_health=player_health, locked=locked, unlocks=unlocks))
	
		return level_lines

	def handle_key_up(self, key):
		# Escape should mean return to the launch screen
		if key == K_ESCAPE:
			self._go_to_launch_screen()
	
	def _go_to_launch_screen(self):
			self._screen_manager.set(lambda *a: LaunchScreen(*a, picker_screen_factory=LevelPickerScreen))
	
	def handle_click(self):			
		# Check special links first
		if self.next_button != None and self.next_button.is_hovered:
			self._screen_manager.set(lambda *a: LevelPickerScreen(*a, page=self._page + 1, _cached_level_lines=self.level_lines))
			return # We've done what we needed to
		elif self.back_button.is_hovered():
			self._screen_manager.go_back()
			return
		
		unlocked_levels = settingsmanager.use_json(lambda json: json[Keys.UNLOCKED_LEVELS_KEY])
		
		# Find the valid element that is at that position
		clicked = [ll for ll in self._get_lines_for_page() if not ll.is_header and ll.el.is_hovered and (not ll.locked or ll.file_path in unlocked_levels)]
		
		# If the user didn't click on anything, don't do anything
		if len(clicked) != 1:
			return
			
		# Now, we only want to keep arround that single element		
		self._play_level(clicked[0])
		
	def _play_level(self, data):
		# Create callback functions
		win = lambda total_rings, my_rings, my_health: self._on_level_won(data, total_rings, my_rings, my_health)
		lose = lambda: self._on_level_lost(data)
		restart = lambda: self._play_level(data)
		def quit():
			self._add_to_failed(data)
			self._screen_manager.go_back() # Returns from the pause menu to the game
			self._screen_manager.go_back() # Returns from the game to the level picker
		
		# Now set the screen to the chosen level!
		self._screen_manager.set(lambda surface, screen_size, screen_manager: LevelScreen(surface, screen_size, screen_manager, data.name, data.file_path, data.player_health, win, lose, quit, restart))
	
	def _add_to_failed(self, data):
		def update_json_data(json):		
			# Update the data that needs to be
			if not data.file_path in json[Keys.COMPLETED_LEVELS_KEY] and not data.file_path in json[Keys.FAILED_LEVELS_KEY]:
				json[Keys.FAILED_LEVELS_KEY].append(data.file_path)
				return True
		
		settingsmanager.perform_update(update_json_data)
		
	def _go_to_me(self):
		# Set the screen to this object
		self._page = 0 # Reset the page state
		self._screen_manager.set(lambda *args: self)
		
	def _on_level_won(self, data, total_rings, my_rings, my_health):
		def update_json_data(json):
			data_changed = False
			
			# Shortcut names
			failed = json[Keys.FAILED_LEVELS_KEY]
			completed = json[Keys.COMPLETED_LEVELS_KEY]
			
			# Add the file to the completed levels array		
			if data.file_path not in completed or completed[data.file_path][Keys.COMPLETED_LEVEL_MY_RINGS_KEY] < my_rings or completed[data.file_path][Keys.COMPLETED_LEVEL_MY_HEALTH_KEY] < my_health:
				completed[data.file_path] = {}
				completed[data.file_path][Keys.COMPLETED_LEVEL_MY_RINGS_KEY] = my_rings
				completed[data.file_path][Keys.COMPLETED_LEVEL_TOTAL_RINGS_KEY] = total_rings
				completed[data.file_path][Keys.COMPLETED_LEVEL_MY_HEALTH_KEY] = my_health
				data_changed = True
				
			# Remove it from the failed array
			if data.file_path in failed:
				failed.remove(data.file_path)
				data_changed = True
				
			# Record all of the levels this unlocks as unlocked
			for map_path in data.unlocks:
				if map_path not in json[Keys.UNLOCKED_LEVELS_KEY]:
					json[Keys.UNLOCKED_LEVELS_KEY].append(map_path)
					data_changed = True
			
			# Update the data file if need be
			return data_changed
			
		settingsmanager.perform_update(update_json_data)
			
		# Show the end game screeen
		completion_percentage = self._calculate_completion_percentage(my_rings, total_rings, my_health, data.player_health)
		self._screen_manager.set(lambda surface, screen_size, screen_manager: GameWonScreen(surface, screen_size, screen_manager, lambda: self._play_level_again(data), completion_percentage))
		
	def _on_level_lost(self, data):		
		self._add_to_failed(data)
		# Show the end game screen
		self._screen_manager.set(lambda surface, screen_size, screen_manager: GameLostScreen(surface, screen_size, screen_manager, lambda: self._play_level_again(data)))
		
	def _play_level_again(self, data):
		self._screen_manager.go_back()
		self._screen_manager.go_back()
		self._play_level(data)
	
	def _calculate_completion_percentage_from_data_file(self, json, map_file_path, level_health):
		# Get the score data for this level
		level_data = json[Keys.COMPLETED_LEVELS_KEY][map_file_path]
		my_rings = level_data[Keys.COMPLETED_LEVEL_MY_RINGS_KEY]
		total_rings = level_data[Keys.COMPLETED_LEVEL_TOTAL_RINGS_KEY]
		my_health = level_data[Keys.COMPLETED_LEVEL_MY_HEALTH_KEY]
		
		return self._calculate_completion_percentage(my_rings, total_rings, my_health, level_health)
	
	def _calculate_completion_percentage(self, my_rings, total_rings, my_health, total_health):		
		# Calculate the percentage for the ring completion
		ring_percentage = int((my_rings/total_rings)*100) if total_rings != 0 else 100
		# And the percentage for the health at the end
		health_percentage = int(my_health/total_health*100)
		
		# The completeion percentage is the average of the two percentages
		return int((ring_percentage + health_percentage)/2)
		
	def _get_lines_for_page(self):
		lines_per_page = (self.screen_size[1] / LINE_HEIGHT) - 1
		
		min = (self._page) * lines_per_page
		max = (self._page + 1) * lines_per_page
	
		self._is_last_page = False
		headers_so_far = 0
		
		for i, line in enumerate(self.level_lines):
			if line.is_header:
				headers_so_far += 1
		
			if (i + headers_so_far) >= max: break # We're done!
			if (i + headers_so_far) < min:	continue # Not there yet...
				
			if line.is_header:
				# Return a blank line for sizing
				yield LevelLine("", is_header=True)
			
			# Return the actual line
			yield line
			
			if i == len(self.level_lines): 
				self._is_last_page = True

		
	def render(self, refresh_time):
		# Set the backgroud color
		self.shape_renderer.render_rect((0, 0, self.screen_size[0], self.screen_size[1]), color=colors.DARK_GRAY)
		
		# Show the mouse on the levels screen
		pygame.mouse.set_visible(True)
			
		unlocked = settingsmanager.use_json(lambda json: json[Keys.UNLOCKED_LEVELS_KEY])
		completed = settingsmanager.use_json(lambda json: json[Keys.COMPLETED_LEVELS_KEY])
		failed = settingsmanager.use_json(lambda json: json[Keys.FAILED_LEVELS_KEY])
		
		# Render each line
		for i, line in enumerate(self._get_lines_for_page()):
			el_pos = (INNER_LEFT if line.is_header else OUTER_LEFT, LINE_HEIGHT * (i - (0.5 if line.is_header else 0.25)))
			
			# Render the line appropriately
			if line.is_header:
				el = self.package_text_renderer.render(line.name, el_pos, color=colors.WHITE)		
			
			elif line.locked and line.file_path not in unlocked:
				# Redner a single color element with no hover color
				el = self.level_text_renderer.render(line.name, el_pos, color=colors.MID_GRAY, hover_color=colors.MID_GRAY)
			
				# Render a Lock icon next to the name
				self.sprite_renderer.render(LockedIcon(INNER_LEFT, LINE_HEIGHT * i)) 
			
			elif line.file_path in completed:		
				# Get the completeion percentage
				completion_percentage = settingsmanager.use_json(lambda json: self._calculate_completion_percentage_from_data_file(json, line.file_path, line.player_health))
			
				# Create a row for the level including the completion percentage.
				line_text = line.name + " (" + str(completion_percentage) + "%)"
				
				# Now, render that line
				el = self.level_text_renderer.render(line_text, el_pos, color=colors.MID_GREEN, hover_color=colors.PALE_GREEN)
				
				# Render a Completed icon to the left of the name
				self.sprite_renderer.render(CompletedIcon(INNER_LEFT, LINE_HEIGHT * i)) 
			
			elif line.file_path in failed:
				el = self.level_text_renderer.render(line.name, el_pos, color=colors.RED, hover_color=colors.TOMATO)
				
				# Render a Failed icon to the left of the name
				self.sprite_renderer.render(FailedIcon(INNER_LEFT, LINE_HEIGHT * i)) 
			
			else: # Just render a standard level line
				el = self.level_text_renderer.render(line.name, el_pos, color=colors.SILVER)
			
			# Finally, store the rendered elemenet for click handling
			line.set_el(el)
		
		# Render special links
		self.back_button = self.sprite_renderer.render(BackIcon(self.screen_size[0] - self.screen_size[0]/8, self.screen_size[1]/8))
		
		# Render the More button if there is more.
		if not self._is_last_page:
			next_link_pos = (self.screen_size[0] - fonts.LINK_TEXT_SIZE * 4, self.screen_size[1] - fonts.LINK_TEXT_SIZE * 2)
			self.next_button = self.link_text_renderer.render(resources.NEXT_LEVEL_PAGE, next_link_pos, color=colors.LIGHT_GRAY, hover_color=colors.SILVER)
