# Jake Thurman
# CIS 226 Game Scripting
# Assignment 3
# 4/24/16

"""
	Project Todos:
		- Add a health status bar
		- Consider adding a mini map
		- Add a "You Won" screen.
		- Explain the controls somewhere
		- Conider adding an in game level designer
"""


import pygame, sys
from pygame.locals import *
from splashscreen import SplashScreen
from sidescrollscreen import SideScrollLevelPickerScreen
from screen import ScreenManager

def main():
	pygame.init()
	
	# Initialize the window
	screen_size = (700, 500)
	DISPLAYSURF = pygame.display.set_mode(screen_size, 0, 32)
	pygame.display.set_caption('Take It Back')
	
	# Create a screen manager object
	# This will handle switching from screen to screen for us
	manager = ScreenManager(DISPLAYSURF, screen_size)
	
	# We want to start with the splash screen
	manager.set(SplashScreen)
	# Then, on click, we want to set the screen to the side scroller screen.
	# This is a weird looking line, I know, but bare with it.
	# We first take the current screen (the SplashScreen we just set) using manager.get(),
	# We then tell the screen that when we click it, (set_on_click) to call our lambda.
	# that lambda gives the manager a new screen using manager.set. The lambda that we pass in there
	# is a factory to create a new SideScrollLevelPickerScreen with those two parameters.
	manager.get().set_on_click(lambda: manager.set(lambda surf, size: SideScrollLevelPickerScreen(surf, size, manager.set)))
	
	# Run the "game loop"
	while True:		
		# Get any current events
		for event in pygame.event.get():
			# If this is a quit event
			if event.type == QUIT:
				# Quit pygame and then the whole program
				pygame.quit()
				sys.exit()
			elif event.type == MOUSEBUTTONDOWN:
				manager.handle_click()
			elif event.type == KEYDOWN:
				manager.handle_key_down(event.key)
			elif event.type == KEYUP:
				manager.handle_key_up(event.key)			
		
		# Refresh the display as needed
		manager.render()
		pygame.display.update()

# Run the Script!
if __name__ == '__main__':
	main()
