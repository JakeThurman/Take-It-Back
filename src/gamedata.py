class Data(object):
	def __init__(self, surface, screen_size, screen_manager):
		self._surface = surface
		self._screen_size = screen_size
		self._screen_manager = screen_manager
		
	def get_surface(self):
		return self._surface
		
	def get_screen_size(self):
		return self._screen_size
		
	def get_screen_manager(self):
		return self._screen_manager