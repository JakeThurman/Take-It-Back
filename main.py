# Jake Thurman
# CIS 226 Game Scripting
# Assignment 3
# 4/24/16

"""
	Project TODOs/Ideas:
		- BUGS:
			- Baddie movement calculation is just awful
			- Make level picker screen scroll so you can have more than ~10 levels
		
		- Add quit button to SideScrollLevelPickerScreen
		
		- Add "?" or "HELP" button whick explains controls 
			- SideScrollLevelPickerScreen
			- PauseMenuScreen
			
		- Add pause button to level screen
		
		- Add mini map at bottom right
"""


import pygame, sys, resources
from pygame.locals import *
from splashscreen import SplashScreen
from levelpickerscreen import LevelPickerScreen
from screen import ScreenManager

def main(FPS):
	pygame.init()
	
	# Initialize the window
	screen_size = (700, 500)
	DISPLAYSURF = pygame.display.set_mode(screen_size, 0, 32)
	pygame.display.set_caption(resources.GAME_TITLE)
	
	# Create a screen manager object
	# This will handle switching from screen to screen for us
	manager = ScreenManager(DISPLAYSURF, screen_size)
	
	# On click of the splash screen, we want to set the screen to the side scroller screen.
	# This is a weird looking line, I know, but bare with it.
	# We first take the current screen (the SplashScreen we just set) using manager.get(),
	# We then tell the screen that when we click it, (set_on_click) to call our lambda.
	# that lambda gives the manager a new screen using manager.set. The lambda that we pass in there
	# is a factory to create a new SideScrollLevelPickerScreen with those two parameters.
	click_event = lambda: manager.set(lambda surf, size: LevelPickerScreen(surf, size, manager.set))
	
	# We want to start with the splash screen
	manager.set(lambda surf, size: SplashScreen(surf, size, click_event))
	
	# FPS manager
	clock = pygame.time.Clock()
	
	# Run the "game loop"
	while True:	
		# Get any current events
		for event in pygame.event.get():
			# If this is a quit event
			if event.type == QUIT:
				# Quit pygame and then the whole program
				pygame.quit()
				sys.exit()
			# Propigate mouse events to the screen manager
			elif event.type == MOUSEBUTTONDOWN:
				manager.handle_click()
			elif event.type == KEYDOWN:
				manager.handle_key_down(event.key)
			elif event.type == KEYUP:
				manager.handle_key_up(event.key)			
		
		# Tell the pygame clock what we want the FPS to be
		# this in turn responds with the time since the  
		# last frame update which we provide to render().
		refresh_time = clock.tick(FPS) 
		
		# Refresh the display as needed
		manager.render(refresh_time)
		pygame.display.update()

# Run the Script!
if __name__ == '__main__':
	FPS = 45 # The constant refresh time
	main(FPS)
