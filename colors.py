# Jake Thurman
# CIS-226 Game Scripting
# Color constants
BLACK = (0,0,0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
SKY_BLUE = (0, 191, 255)
LIGHT_GRAY = (150, 150, 150)
MID_GRAY = (100, 100, 100)
DARK_GRAY = (50, 50, 50)
DARK_GREEN = (0,100,0)
MID_GREEN = (72, 231, 84)
PALE_GREEN = (152,251,152)
TOMATO = (255,80,70)
SILVER = (194, 194, 194)


# Convers an image to the grayscale equivenlent
def to_grayscale(image):
	width, height = image.get_size() 
	for x in range(width): 
		for y in range(height): 
			red, green, blue, alpha = image.get_at((x, y)) 
			gs = 0.3 * red + 0.59 * green + 0.11 * blue 
			image.set_at((x, y), (gs, gs, gs, alpha))