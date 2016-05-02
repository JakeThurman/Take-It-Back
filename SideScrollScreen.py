# Jacob Thurman
# Side Scroller Game Screen

import pygame, sys, colors, json, resources
from rendering import *
from screen import Screen
from sidescrollworld import Level
from pygame.locals import *

# Constants needed by this file
class _consts:
	"""SETTINGS"""
	# Camera should move by thid number of pixels when it adjusts.
	# This nubmer should be low enough to dis-allow jerkiness when 
	# quickly moving up/down, but also low enough to avoid jerking
	# when the player jumps, and trying to rerender that each time
	CAMERA_ADJUST_PIXELS = 25 
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
	
class SideScrollLevelPickerScreen(Screen):
	"""Handles picking a side scroller game"""

	# Constructor
	# NOTE: This c'tor is not a legal Screen.ScreenManger factory
	def __init__(self, surface, screen_size, set_screen_func):		
		# Create dependencies
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
		# Now set the screen to the chosen level!
		self._set_screen_func(lambda surface, screen_size: SideScrollScreen(surface, screen_size, file_path, player_health, lambda is_win: self._on_level_complete(is_win, file_path, player_health)))
	
	def _go_to_me(self):
		# Set the screen to this object
		self._set_screen_func(lambda surface, screen_size: self)
	
	def _on_level_complete(self, is_win, file_path, player_health):
		data_changed= False
		
		# Shortcuts!
		failed = self.json_data[_consts.FAILED_LEVELS_KEY]
		completed = self.json_data[_consts.COMPLETED_LEVELS_KEY]
		
		if is_win:
			# Add the file to the completed levels array
			if not file_path in completed:
				completed.append(file_path)
				data_changed = True
				
			# Remove it from the failed array
			if file_path in failed:
				failed.remove(file_path)
				data_changed = True
		
		elif not file_path in completed and not file_path in failed:
			failed.append(file_path)
			data_changed = True
		
		if data_changed:
			# Update the data file with new data
			with open(_consts.JSON_DATA_FILE_NAME, 'w') as outfile:
				json.dump(self.json_data, outfile, indent=2)
		
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
				el = self.level_text_renderer.render(line.name, el_pos, color=colors.MID_GREEN, hover_color=colors.PALE_GREEN)
				self.sprite_renderer.render(CompletedIcon(INNER_LEFT, el_pos[1]))
			elif line.el != None and line.file_path in self.json_data[_consts.FAILED_LEVELS_KEY]:
				el = self.level_text_renderer.render(line.name, el_pos, color=colors.RED, hover_color=colors.TOMATO)
				self.sprite_renderer.render(FailedIcon(INNER_LEFT, el_pos[1]))
			else:
				el = self.level_text_renderer.render(line.name, el_pos, color=colors.SILVER)
			
			# Finally, store the rendered elemenet for click handling
			line.set_el(el)

class EndGameScreen(Screen):
	"""The game has ended here is what we say..."""

	def __init__(self, surface, screen_size, is_win, return_to_picker_screen_func, play_again_func):
		self.option_renderer = OptionRenderer(surface, pygame.font.SysFont("monospace", 30))
		self.shape_renderer = ShapeRenderer(surface)
		self.screen_size = screen_size
		self.is_win = is_win
		self.return_to_picker_screen_func = return_to_picker_screen_func
		self.play_again_func = play_again_func
		self.set_on_click(self._click_handler)
		
	def _click_handler(self):
		# Do the requested action!
		if self.return_to_level.is_hovered:
			self.return_to_picker_screen_func()
		elif self.play_again.is_hovered:
			self.play_again_func()
	
	def render(self, refresh_time):
		# Set the backgroud color
		self.shape_renderer.render_rect((0, 0, self.screen_size[0], self.screen_size[1]), color=colors.DARK_GRAY, alpha=30)
		
		pygame.mouse.set_visible(True)	# Show the mouse on the levels screen
		
		# Take the correct message 
		message = resources.YOU_WON if self.is_win else resources.YOU_LOST
		
		# The position for the "you won/lost" message
		pos = (self.screen_size[0]/8, self.screen_size[1]/8)
		
		# Render the "you won/lost" message
		self.option_renderer.render(message, pos, color=colors.WHITE, hover_color=colors.WHITE)
		
		# Render the links at the bottom (pick a level and play again)
		self.return_to_level = self.option_renderer.render(resources.RETURN_TO_LEVEL_PICKER, (pos[0], self.screen_size[1]-pos[1]), color=colors.SILVER)
		self.play_again = self.option_renderer.render(resources.PLAY_AGAIN, (pos[0], self.screen_size[1]-(2*pos[1])), color=colors.SILVER)

class StatusBar:
	"""The side scroll game status bar"""
	# Constants
	HEIGHT = 15
	
	def __init__(self, surface, screen_size, player):
		self.shape_renderer = ShapeRenderer(surface)
		self.player = player
		self.screen_size = screen_size
	
	def _get_curr_color(self):
		# We want to draw the health bar as green normally, but
		# red if it is bellow one quarter of the initial health
		# level and yellow in bettween one quarer and two thrids
		
		if (self.player.initial_health / 4) >= self.player.health:
			return colors.RED
		elif (self.player.initial_health / 3) * 2 >= self.player.health:
			return colors.YELLOW
		else:
			return colors.GREEN
	
	def render(self):		
		# Pad the screen by one 8th of the total size (for the left, right and bottom)
		padding = (self.screen_size[0] / 8, self.screen_size[1] / 16)
		
		full_bar_size = (padding[0], self.screen_size[1] - (self.HEIGHT + padding[1]), self.screen_size[0] - (2 * padding[0]), self.HEIGHT)
		
		# Draw the full bar
		self.shape_renderer.render_rect(full_bar_size, color=colors.BLACK)
		
		# Draw the current health bar overtop
		self.shape_renderer.render_rect((full_bar_size[0], full_bar_size[1], full_bar_size[2] * (self.player.health/self.player.initial_health), full_bar_size[3]), color=self._get_curr_color())

class SideScrollScreen(Screen):
	"""Handles rendering of the actual side scrolling game"""
	
	# Constructor
	# NOTE: This c'tor is not a legal Screen.ScreenManger factory
	def __init__(self, surface, screen_size, level_file, player_health, on_end_func):		
		# Store the passed in values (we don't surface as a global)
		self.screen_size = screen_size;
		self.on_end_func = on_end_func
		
		# Create dependencies
		self.shape_renderer = ShapeRenderer(surface)
		
		# Create a level object
		self.my_level = Level(level_file, player_health)
		self.my_level.init()
		
		# Create a camera object
		level_size = self.my_level.get_size()
		self.camera = Camera(surface, self.my_level.player.rect, level_size[0], level_size[1], _consts.CAMERA_ADJUST_PIXELS)
		
		# Create a status bar renderer
		self.status_bar = StatusBar(surface, screen_size, self.my_level.player)
		
		# Initialize key handling
		self.up = self.down = self.left = self.right = False
		
		self.bullets = []
	
	# Handles pygame key change events
	def _handle_key_change(self, key, value):
		if key == K_UP or key == K_SPACE:
			self.up = value
		elif key == K_DOWN:
			self.down = value
		elif key == K_LEFT:
			self.left = value
		elif key == K_RIGHT:
			self.right = value
	
	# Handles key up events, and clears the stored value for any of the keys we were listening for
	def handle_key_up(self, key):
		self._handle_key_change(key, False)
		
		# if this is the escaple key, go back to the main menu
		if key == K_ESCAPE:
			self.on_end_func(False) # is_win = False
	
	# Handles key down events, and stores a flag for any of the keys we are listening for
	def handle_key_down(self, key):
		self._handle_key_change(key, True)
	
	def _add_bullet(self, bullet):
		self.my_level.all_sprite.add(bullet)
		self.bullets.append(bullet)
		
	def _on_bullet_die(self, bullet):
		self.my_level.all_sprite.remove(bullet)
		self.bullets.remove(bullet)
	
	# Renders a side scoller display
	def render(self, refresh_time):
		# Check if the player has one. If they have, 
		# call on_end_func() and return; we're done.
		if self.my_level.player.has_won(self.my_level.win_blocks):		
			self.on_end_func(True) # is_win = True
			return
		
		# Set the backgroud to sky blue
		self.shape_renderer.render_rect((0, 0, self.screen_size[0], self.screen_size[1]), color=colors.SKY_BLUE)
		
		pygame.mouse.set_visible(False)	# Hide the mouse inside the game
		
		# Render all of the level's sprites
		self.camera.draw_sprites(self.my_level.all_sprite)
		
		# Update the player object based of the currently pressed keys	
		self.my_level.player.update(self.up, self.down, self.left, self.right, self.my_level.world)
		
		# Handle updating spawners
		for spawner in self.my_level.spawners:
			spawner.update(refresh_time, self.my_level.player, self.my_level.world, self._add_bullet)
			
		# Update any currently flying bullets
		for bullet in self.bullets:
			bullet.update(refresh_time, self.my_level.world, self.my_level.player, lambda: self._on_bullet_die(bullet), lambda: self.on_end_func(False)) #self.on_end_func(is_win = false)
		
		# Update the camera position
		self.camera.update()
		
		# Render the status bar - if there is any reason to show it
		if len(self.my_level.spawners) != 0:
			self.status_bar.render()
		
		# Update the pygame display
		pygame.display.flip()
