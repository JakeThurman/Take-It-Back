from pygame import font
from globals import ROOT_PATH

font.init()

LINK_TEXT_SIZE = 25
def COURIER_PRIME_SANS(size=LINK_TEXT_SIZE):
	return font.Font(ROOT_PATH + "fonts\Courier Prime Sans.ttf", size)

def OPEN_SANS(size=LINK_TEXT_SIZE):
	return font.Font(ROOT_PATH + "fonts\OpenSans-Regular.ttf", size)

def KELMSCOT(size=LINK_TEXT_SIZE):
	return font.Font(ROOT_PATH + "fonts\KELMSCOT.ttf", size)
