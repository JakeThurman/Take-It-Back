# Jacob Thurman
# Side Scroller Game Screen

import pygame, sys, colors, json, mouseovermenu
from renderingfactories import *
from Screen import Screen
from SideScroller import Level, Camera
from pygame.locals import *

# Constants needed by this file
class _consts:
	FPS = 45 # The frames per second we always want to render at.
	
	# Camera should move by thid number of pixels when it adjusts.
	# This nubmer should be low enough to dis-allow jerkiness when 
	# quickly moving up/down, but also low enough to avoid jerking
	# when the player jumps, and trying to rerender that each time
	CAMERA_ADJUST_PIXELS = 25 
	
# Helper class, for getting named valus for level links (and header)
class LevelLine:
	def __init__(self, name, is_header = False, file_path=None):
		self.name = name
		self.is_header = is_header
		self.file_path = file_path
		self.el = None
		
	def set_el(self, el):
		self.el = el
	
class SideScrollLevelPickerScreen(Screen):
	"""Handles picking a side scroller game"""

	LEVELS_PREFIX = "levels/"
	JSON_DATA_FILE_NAME = 'levels/data.json'
	PACKAGE_JSON_FILE_NAME = "/package.json"
	
	# Constructor
	# NOTE: This c'tor is not a legal Screen.ScreenManger factory
	def __init__(self, surface, screen_size, set_screen_func):
		super().__init__()
		
		# Create dependencies
		self.package_text_renderer = mouseovermenu.OptionRenderer(surface, pygame.font.Font(None, 40), do_hover=False)
		self.level_text_renderer = mouseovermenu.OptionRenderer(surface, pygame.font.SysFont("monospace", 25))
		self.completed_level_text_renderer = mouseovermenu.OptionRenderer(surface, pygame.font.SysFont("monospace", 25), color=colors.DARK_GREEN, hover_color=colors.PALE_GREEN)
		self.shape_renderer = ShapeRenderer(surface)
		
		# Store passed in values as needed
		self._set_screen_func = set_screen_func
		self.screen_size = screen_size
		
		# Create links to all the levels we need
		# First, get all of the level packages we can use
		with open(self.JSON_DATA_FILE_NAME, "r") as data_file:    
			self.json_data = json.load(data_file)
			
		# Here are all the lines for the levels.
		# This includes levels and headers
		self.level_lines = []
		
		# Next, add each package
		for level_package_path in self.json_data["packages"]:
			# Open the package.json file for this folder
			with open(self.LEVELS_PREFIX + level_package_path + self.PACKAGE_JSON_FILE_NAME) as level_package:
				# Load the package json
				level_package_data = json.load(level_package)
				
				# Create a line for the package header and a blank one for spacing
				self.level_lines.append(LevelLine("", is_header = True))
				self.level_lines.append(LevelLine(level_package_data["name"], is_header = True))
				
				# Now create a line for each actual level.
				for level_data in level_package_data["levels"]:
					# Add a line for the package name
					self.level_lines.append(LevelLine(level_data["name"], file_path=self.LEVELS_PREFIX + level_package_path + "/" + level_data["map"]))
		
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
		
		# Now set the screen to the chosen level!
		self._set_screen_func(lambda surface, screen_size: SideScrollScreen(surface, screen_size, clicked.file_path, lambda is_win: self._on_level_complete(is_win, clicked.file_path)))
	
	def _on_level_complete(self, is_win, file_path):
		# Add the file to the completed object
		if is_win and not file_path in self.json_data["completed"]:
			self.json_data["completed"].append(file_path)
			
			# Dump the json to the save data file
			with open(self.JSON_DATA_FILE_NAME, 'w') as outfile:
				json.dump(self.json_data, outfile, indent=2)
		
		
		# Set the screen to this object
		self._set_screen_func(lambda surface, screen_size: self)
		
	def handle_key_up(self, key):
		if key == K_ESCAPE:
			pygame.quit()
			sys.exit()
		
	def render(self):		
		# Set the backgroud to white
		self.shape_renderer.render_rect((0, 0, self.screen_size[0], self.screen_size[1]), color=colors.SKY_BLUE)
		
		pygame.mouse.set_visible(True)	# Show the mouse on the levels screen
		
		# Render each line
		for i, line in enumerate(self.level_lines):
			# Get the corrent text renderer
			if line.is_header:
				text_renderer = self.package_text_renderer 
			elif line.el != None and line.file_path in self.json_data["completed"]:
				text_renderer = self.completed_level_text_renderer
			else:
				text_renderer = self.level_text_renderer
			
			# Finally, render the line, and store the rendered elemenet for click handling
			line.set_el(text_renderer.render(line.name, (25, i * 30)))

class SideScrollScreen(Screen):
	"""Handles rendering of the actual side scrolling game"""
	
	# Constructor
	# NOTE: This c'tor is not a legal Screen.ScreenManger factory
	def __init__(self, surface, screen_size, level_file, on_end_func):
		# Call parent c'tor
		super().__init__()
		
		# Store the passed in values (we don't surface as a global)
		self.screen_size = screen_size;
		self.on_end_func = on_end_func
		
		# Create dependencies
		self.shape_renderer = ShapeRenderer(surface)
		self.clock = pygame.time.Clock() # Manages FPS
		
		# Create a level object
		self.my_level = Level(level_file)
		self.my_level.init()
		
		# Create a camera object
		level_size = self.my_level.get_size()
		self.camera = Camera(surface, self.my_level.player.rect, level_size[0], level_size[1], _consts.CAMERA_ADJUST_PIXELS)
		
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
	def render(self):
		# Check if the player has one. If they have, 
		# call on_end_func() and return; we're done.
		if self.my_level.player.has_won(self.my_level.win_blocks):
			self.on_end_func(True) # is_win = True
			return
		
		# Set the backgroud to white
		self.shape_renderer.render_rect((0, 0, self.screen_size[0], self.screen_size[1]), color=colors.SKY_BLUE)
		
		pygame.mouse.set_visible(False)	# Hide the mouse inside the game		
		self.clock.tick(_consts.FPS) # Tell the pygame clock what we want the FPS to be
		
		# Render all of the level's sprites
		self.camera.draw_sprites(self.my_level.all_sprite)
		
		# Update the player object based of the currently pressed keys	
		self.my_level.player.update(self.up, self.down, self.left, self.right, self.my_level.world)
		
		# Handle updating spawners
		for spawner in self.my_level.spawners:
			spawner.update(self.my_level.player, self.my_level.world, self._add_bullet)
			
		# Update any currently flying bullets
		for bullet in self.bullets:
			bullet.update(self.my_level.world, self.my_level.player, lambda: self._on_bullet_die(bullet))
		
		# Update the camera position
		self.camera.update()
		
		# Update the pygame display
		pygame.display.flip()
