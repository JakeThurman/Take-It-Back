# Jacob Thurman
# Pygame helper classes for simplified renderering

import pygame, colors
		
class ShapeRenderer:
	"""Renders simple shapes"""
	
	# Constructor
	def __init__(self, surface):
		self.surface = surface
		
	# Draws a pygame circle
	def render_circle(self, pos, r, color=None):
		pygame.draw.circle(self.surface, color, pos, r, 0)
		
	# Draws a pygame rectangle
	def render_rect(self, coords, color=None, alpha=None):
		if alpha == None:
			pygame.draw.rect(self.surface, color, coords) # Draw a basic rectangle
		else:
			s = pygame.Surface((coords[2] - coords[0], coords[3] - coords[1]))            # the size of the rect
			s.set_alpha(alpha)                           # alpha level
			s.fill(color)                                # this fills the entire surface
			self.surface.blit(s, (coords[0], coords[1])) # (0,0) are the top-left coordinates
		
class TextRenderer:
	"""Helper class so that I can add text in one line instead of a bunch!"""
	
	# Constructor
	def __init__(self, color, scale, surface, font):
		self.color = color
		self.scale = scale
		self.surface = surface
		self.font = font

	# Renders a block of text to a given row on the display
	def render(self, text, row, underline=False):
		# Set optional underline property on font object
		self.font.set_underline(underline)	
		# Creates a text object
		text = self.font.render(text, True, self.color)
		# Renders the text to the window
		self.surface.blit(text, (self.scale, row * self.scale))

class Option:
	"""Minimal return data class"""
	def __init__(self, is_hovered):
		self.is_hovered = is_hovered

class OptionRenderer:
	"""Basically TextRenderer but this handles hovering automatically"""
	
	# Constructor
	def __init__(self, surface, font, do_hover=True):
		self.font = font
		self.surface = surface
		self.do_hover = do_hover

	# Renders an option
	def render(self, text, pos, color=colors.MID_GRAY, hover_color=colors.WHITE):
		rect = self._make_rect(text, pos)
		rend = self._do_rend(text, rect, color, hover_color)
		self.surface.blit(rend, rect)
		return Option(self._is_hovered(rect))

	# Rendering Imp'l
	def _do_rend(self, text, rect, color, hover_color):
		return self.font.render(text, True, self._get_color(rect, color, hover_color))

	# Checks if the mouse is over the item
	def _is_hovered(self, rect):
		return rect != None and rect.collidepoint(pygame.mouse.get_pos())
		
	# Get's the color for item including hovering handling
	def _get_color(self, rect, color, hover_color):
		if self.do_hover and self._is_hovered(rect):
			return hover_color
		else:
			return color

	# Makes the outline rectangle for the object
	def _make_rect(self, text, pos):
		rect = self._do_rend(text, None, (0,0,0), (0,0,0)).get_rect()
		rect.topleft = pos
		return rect
		
class Sprite(pygame.sprite.Sprite):
	"""
		Base class for custom sprites classes
	"""
	def __init__(self, x, y, file_name, use_alpha=False):		
		# Init the parent class
		super().__init__()
		
		# Load the image
		self.use_alpha = use_alpha
		self.change_image(file_name)
		
		# Store positional information
		self.x = x
		self.y = y
		self.rect.topleft = [x, y]
		
	def change_image(self, file_name):
		# Update the image
		unconverted_image = pygame.image.load(file_name)
		self.image = unconverted_image.convert_alpha() if self.use_alpha else unconverted_image.convert()
		
		# Update the rect
		self.rect = self.image.get_rect()

class SpriteRenderer:
	"""
		Handlers rendering sprites
	"""
	def __init__(self, surface):
		self.surface = surface
		
	def render(self, sprite, convert_rect=None):
		self.surface.blit(sprite.image, sprite.rect if convert_rect == None else convert_rect(sprite.rect))
		
class Camera:
	"""
		Class for centering the screen on the player
	"""
	def __init__(self, surface, player, level_width, level_height, pixes_to_adjust_by):
		self.player = player
		self.sprite_renderer = SpriteRenderer(surface)
		self.rect = surface.get_rect()
		self.rect.center = self.player.center
		self.world_rect = pygame.Rect(0, 0, level_width, level_height)
		self.pixes_to_adjust_by = pixes_to_adjust_by

	def update(self):
		# Adjust each side to be closer to the player
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
		# Defines a rectangle positioned relitive to the camera position
		return pygame.Rect(rect.x-self.rect.x, rect.y-self.rect.y, rect.w, rect.h)

	def draw_sprites(self, sprites):
		# Draw all of the sprites, relitive to the camera
		for s in sprites:
			if s.rect.colliderect(self.rect): # Only draw if they are in view.
				self.sprite_renderer.render(s, convert_rect=self._rel_rect)
