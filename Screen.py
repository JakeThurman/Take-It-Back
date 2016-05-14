"""Jake Thurman
Screen Helper Classes
"""

import pygame, sys
from pygame.locals import K_ESCAPE

class Screen:
	"""Handles and exposes common screen actions
	"""
	def __init__(self):
		pass # Nothing to do
	
	def render(self, refresh_time):
		raise NotImplementedError("render has no impl")
		
	def handle_click(self):
		pass
		
	def handle_key_down(self, key):
		pass
	
	# By default close the game on key up
	def handle_key_up(self, key):
		if key == K_ESCAPE:
			pygame.quit()
			sys.exit()
		
	
class SafeScreenManager:
	"""Wrapper class for ScreenManager to give write only access to screens
	"""
	def __init__(self, screen_manager):
		"""Constructor
		"""
		self._screen_manager = screen_manager
	
	def set(self, factory):
		self._screen_manager.set(factory)
		
	def go_back(self):
		self._screen_manager.go_back()
		
class ScreenManager:
	"""Super simple helper to manage different screeens with common pass through methods.
	"""
	
	def __init__(self, surface, screen_size):
		"""Constructor
		"""
		self.surface = surface
		self.screen_size = screen_size
		self.prev = []
		self.curr = None
	
	def go_back(self):
		"""Returns to the previous screen
		"""
		assert len(self.prev) > 0
		self.curr = self.prev.pop()
	
	def set(self, factory):
		"""Sets the current screen using a factory/c'tor
		"""
		# Add the screen we are on before the revert to the history stack.
		if self.curr != None:
			self.prev.append(self.curr)
		# Create the new screen
		self.curr = factory(self.surface, self.screen_size, SafeScreenManager(self))
		# Throw an exception if the factory returned an invalid result
		assert self.curr != None
	
	# Pass through methods :::
	def render(self, refresh_time):
		assert self.curr != None
		self.curr.render(refresh_time)
	
	def set_on_click(self, handler):
		assert self.curr != None
		self.curr.set_on_click(handler)

	def handle_click(self):
		assert self.curr != None
		self.curr.handle_click()
	
	def handle_key_down(self, key):
		assert self.curr != None
		self.curr.handle_key_down(key)
			
	def handle_key_up(self, key):
		assert self.curr != None
		self.curr.handle_key_up(key)
