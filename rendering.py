"""Pygame helper classes for simplified renderering
Jacob Thurman
"""

import pygame, colors
		
class ShapeRenderer:
	"""Renders simple shapes
	"""
	
	def __init__(self, surface):
		"""Constructor
		"""
		self.surface = surface
	
	def render_circle(self, pos, r, color=None):
		"""Draws a pygame circle
		"""
		pygame.draw.circle(self.surface, color, pos, r, 0)
	
	def render_rect(self, coords, color=None, alpha=None):
		"""Draws a pygame rectangle
		"""
		if alpha == None:
			pygame.draw.rect(self.surface, color, coords) # Draw a basic rectangle
		else:
			s = pygame.Surface((coords[2] - coords[0], coords[3] - coords[1])) # the size of the rect
			s.set_alpha(alpha)                           # alpha level
			s.fill(color)                                # this fills the entire surface
			self.surface.blit(s, (coords[0], coords[1])) # set the top-left coordinates

class Option:
	"""Minimal return data class
	"""
	def __init__(self, is_hovered):
		self.is_hovered = is_hovered

class OptionRenderer:
	"""Basically TextRenderer but this handles hovering automatically
	"""
	
	def __init__(self, surface, font, do_hover=True):
		"""Constructor
		"""
		self.font = font
		self.surface = surface
		self.do_hover = do_hover

	def render(self, text, pos, color=colors.MID_GRAY, hover_color=colors.WHITE):
		""" Renders an option
		"""
		rect = self._make_rect(text, pos)
		rend = self._do_rend(text, rect, color, hover_color)
		self.surface.blit(rend, rect)
		return Option(self._is_hovered(rect))

	def _do_rend(self, text, rect, color, hover_color):
		"""Rendering Imp'l
		"""
		return self.font.render(text, True, self._get_color(rect, color, hover_color))

	def _is_hovered(self, rect):
		"""Checks if the mouse is over the item
		"""
		return rect != None and rect.collidepoint(pygame.mouse.get_pos())
	
	def _get_color(self, rect, color, hover_color):
		"""Get's the color for item including hovering handling
		"""
		if self.do_hover and self._is_hovered(rect):
			return hover_color
		else:
			return color
	
	def _make_rect(self, text, pos):
		"""Makes the outline rectangle for the object
		"""
		rect = self._do_rend(text, None, (0,0,0), (0,0,0)).get_rect()
		rect.topleft = pos
		return rect
		
class Sprite(pygame.sprite.Sprite):
	"""Base class for custom sprites classes
	"""
	
	def __init__(self, x, y, file_name, use_alpha=False, grayscale=False):
		"""C'tor
		"""
		# Init the parent class
		super().__init__()
		
		# Load the image
		self._use_alpha = use_alpha
		self._grayscale = grayscale
		self._change_image(file_name)
		
		# Store positional information
		self.x = x
		self.y = y
		self.rect.topleft = [x, y]
		
	def _change_image(self, file_name):
		"""Updates the image of the sprite
		"""
		# Update the image
		unconverted_image = pygame.image.load(file_name)
		self.image = unconverted_image.convert_alpha() if self._use_alpha else unconverted_image.convert()
		
		# Convert to grayscale if needed
		if self._grayscale:
			colors.to_grayscale(self.image)
		
		# Update the rect
		self.rect = self.image.get_rect()
		
	def is_hovered(self):
		return self.rect.collidepoint(pygame.mouse.get_pos())

class SpriteRenderer:
	"""Handlers rendering sprites
	"""
	def __init__(self, surface):
		"""C'tor
		"""
		self.surface = surface
		
	def render(self, sprite, convert_rect=None):
		"""Renders the sprite to the screen
		"""
		self.surface.blit(sprite.image, sprite.rect if convert_rect == None else convert_rect(sprite.rect))
		return sprite
		
class Camera:
	"""Class for centering the screen on the player
	"""
	def __init__(self, surface, player, level_width, level_height, pixes_to_adjust_by):
		"""C'tor
		"""
		self.player = player
		self.sprite_renderer = SpriteRenderer(surface)
		self.rect = surface.get_rect()
		self.rect.center = self.player.center
		self.world_rect = pygame.Rect(0, 0, level_width, level_height)
		self.pixes_to_adjust_by = pixes_to_adjust_by

	def update(self):
		"""Adjusts each side to follow the player
		"""
		if self.player.centerx > self.rect.centerx + self.pixes_to_adjust_by:
			self.rect.centerx = self.player.centerx - self.pixes_to_adjust_by
		if self.player.centerx < self.rect.centerx - self.pixes_to_adjust_by:
			self.rect.centerx = self.player.centerx + self.pixes_to_adjust_by
		if self.player.centery > self.rect.centery + self.pixes_to_adjust_by:
			self.rect.centery = self.player.centery - self.pixes_to_adjust_by
		if self.player.centery < self.rect.centery - self.pixes_to_adjust_by:
			self.rect.centery = self.player.centery + self.pixes_to_adjust_by
			self.rect.clamp_ip(self.world_rect)
	
	def _rel_rect(self, rect):
		"""Defines a rectangle positioned relitive to the camera position
		"""
		return pygame.Rect(rect.x-self.rect.x, rect.y-self.rect.y, rect.w, rect.h)

	def can_see(self, sprite):
		"""Can the camera see this sprite?
		"""
		return sprite.rect.colliderect(self.rect)
		
	def draw_sprites(self, sprites):
		"""Draws all of the sprites, relitive to the camera
		"""
		for s in sprites:
			if self.can_see(s): # Only draw if they are in view.
				self.sprite_renderer.render(s, convert_rect=self._rel_rect)
