"""Hey, Welcome to the code for the game.

If there's anything I can help you with, let me know.

My email is: jacob@thurmans.com
Thanks!
"""

import pygame, sys, resources
from pygame.locals import *
from launchscreen import LaunchScreen
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
	
	# Create a lambda event to use as a "start game" callback for the launch screen.
	start_game = lambda: manager.set(lambda surf, size: LevelPickerScreen(surf, size, manager.set))
	
	# We want to start with the launcher screen
	manager.set(lambda surf, size: LaunchScreen(surf, size, start_game))
	
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
