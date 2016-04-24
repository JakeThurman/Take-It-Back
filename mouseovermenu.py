import pygame, colors

# Minimal return data class
class Option: 
	def __init__(self, is_hovered):
		self.is_hovered = is_hovered

# Handlers hovering automatically
class OptionRenderer:
	def __init__(self, surface, font, do_hover = True, color=colors.MID_GRAY, hover_color=colors.WHITE):
		self.font = font
		self.surface = surface
		self.do_hover = do_hover
		self.color = color
		self.hover_color = hover_color

	def render(self, text, pos):
		rect = self._make_rect(text, pos)
		rend = self._do_rend(text, rect)
		self.surface.blit(rend, rect)
		return Option(self._is_hovered(rect)) 

	def _do_rend(self, text, rect):
		return self.font.render(text, True, self._get_color(rect))

	def _is_hovered(self, rect):
		return rect != None and rect.collidepoint(pygame.mouse.get_pos())
		
	def _get_color(self, rect):
		if self.do_hover and self._is_hovered(rect):
			return self.hover_color
		else:
			return self.color

	def _make_rect(self, text, pos):
		rect = self._do_rend(text, None).get_rect()
		rect.topleft = pos
		return rect