"""Hey, Welcome to the code for the game.

If there's anything I can help you with, let me know.

My email is: jacob@thurmans.com
Thanks!
"""

import pygame, sys, resources, datetime, logging
from tkinter import messagebox
from pygame.locals import *
from launchscreen import LaunchScreen
from levelpickerscreen import LevelPickerScreen
from screen import ScreenManager

def main():
	pygame.init()
	
	# Initialize the window
	screen_size = (700, 500)
	DISPLAYSURF = pygame.display.set_mode(screen_size, 0, 32)
	pygame.display.set_caption(resources.GAME_TITLE)
	
	# Create a screen manager object
	# This will handle switching from screen to screen for us
	manager = ScreenManager(DISPLAYSURF, screen_size)
	
	# Create a lambda event to use as a "start game" callback for the launch screen.
	start_game = lambda: manager.set(LevelPickerScreen)
	
	# We want to start with the launcher screen
	manager.set(lambda surf, size, _: LaunchScreen(surf, size, start_game))
	
	# FPS manager
	clock = pygame.time.Clock()
	FPS = 45 # The constant refresh time
	
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
	# Configure the log file
	logging.basicConfig(filename='dev/errors.log')
	
	# Run the main loop and wait for exceptions
	try:
		main()
	except SystemExit: # Don't log SystemExit exceptions (thrown by sys.exit())
		pass
	except:	
		# Log the exception to the log file
		logging.exception("Date:" + datetime.datetime.now().isoformat())
		
		# Exit pygame
		pygame.quit()
		
		# Alert the user that something bad happened
		messagebox.showerror(resources.AN_EXCEPTION_OCCURED_TITLE, resources.AN_EXCEPTION_OCCURED)
		