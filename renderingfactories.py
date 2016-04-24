# Jacob Thurman
# Pygame helper classes for simplified renderering

import pygame

class TextRenderer:
	'''Helper class so that I can add text in one line instead of a bunch!'''
	
	# Constructor
	def __init__(self, color, scale, surface, font):
		self.color = color
		self.scale = scale
		self.surface = surface
		self.font = font

	# Renders a block of text to a given row on the display
	def render(self, text, row, underline = False):
		# Set optional underline property on font object
		self.font.set_underline(underline)	
		# Creates a text object
		text = self.font.render(text, True, self.color)
		# Renders the text to the window
		self.surface.blit(text, (self.scale, row * self.scale))
		
class ShapeRenderer:
	'''Renders simple shapes'''
	
	# Constructor
	def __init__(self, surface):
		self.surface = surface
		
	# Draws a pygame circle
	def render_circle(self, pos, r, color = None):
		pygame.draw.circle(self.surface, color, pos, r, 0)
		
	# Draws a pygame rectangle
	def render_rect(self, coords, color = None):
		pygame.draw.rect(self.surface, color, coords)