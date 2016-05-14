"""This file contains shared icons
"""

from rendering import Sprite

class BackIcon(Sprite):
	"""A simple back arrow icon.
	"""
	def __init__(self, x, y):
		super().__init__(x, y, "images/icons/back-arrow.png", use_alpha=True)