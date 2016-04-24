# Jake Thurman
# CIS-226 Game Scripting
# Screen Helper Classes
class Screen:
	'''Handles common screen actions'''
	def __init__(self):
		# Set the click function to a dummy lambda by default
		self.click_func = lambda: None
	
	def render(self):
		raise NotImplementedError("render has no impl")
	
	def set_on_click(self, click_func):
		# Store the onclick event
		self.click_func = click_func
		
	def handle_click(self):
		self.click_func()
		
	def handle_key_down(self, key):
		pass
	
	def handle_key_up(self, key):
		pass
		
class ScreenManager:
	'''Super simple helper to manage different screeens with common pass through methods.'''
	
	# Constructor.
	def __init__(self, surface, screen_size):
		self.surface = surface
		self.screen_size = screen_size
		self.curr = None
	
	# Sets the current screen using a factory/c'tor
	def set(self, factory):
		# Create the new screen
		self.curr = factory(self.surface, self.screen_size)
	
	# Returns the current screen instance
	def get(self):
		return self.curr
	
	# Pass through methods :::
	def render(self):
		if self.curr != None:
			self.curr.render()
			
	def handle_click(self):
		if self.curr != None:
			self.curr.handle_click()
	
	def handle_key_down(self, key):
		if self.curr != None:
			self.curr.handle_key_down(key)
			
	def handle_key_up(self, key):
		if self.curr != None:
			self.curr.handle_key_up(key)