"""This file contains shared icons
"""

from rendering import Sprite
import globals as g

class BackIcon(Sprite):
	"""A simple back arrow icon.
	"""
	def __init__(self, x, y):
		super().__init__(x, y, g.ROOT_PATH + "images/icons/back-arrow.png", use_alpha=True)