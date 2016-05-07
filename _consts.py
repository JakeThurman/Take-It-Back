"""
	The file stores constants needed by the game
"""

"""SETTINGS"""
# Camera should move by thid number of pixels when it adjusts.
# This nubmer should be low enough to dis-allow jerkiness when 
# quickly moving up/down, but also low enough to avoid jerking
# when the player jumps, and trying to rerender that each time
CAMERA_ADJUST_PIXELS = 25 
# The default player health when none is specifically specified
DEFAULT_PLAYER_HEALTH = 20

"""LEVEL FILES"""
# The folder where levels are stored
LEVELS_PREFIX = "levels/"
# The path to the data file
JSON_DATA_FILE_NAME = "levels/data.json"
# The name of a package
PACKAGE_JSON_FILE_NAME = "/package.json"

"""JSON KEYS"""
# data.json: The json key for completed items
COMPLETED_LEVELS_KEY = "completed"
# data.json: The total rings for a completed level
COMPLETED_LEVEL_TOTAL_RINGS_KEY = "total-rings"
# data.json: The rings found for a completed level
COMPLETED_LEVEL_MY_RINGS_KEY = "rings"	
# data.json: The json key for failed items
FAILED_LEVELS_KEY = "failed"
# data.json: The json key for all of the packages
PACKAGES_KEY = "packages"
# package.json: The name of this package
PACKAGE_NAME_KEY = "name"
# package.json: The levels in this package
PACKAGE_LEVELS_KEY = "levels"
# package.json: The name of this level
LEVEL_NAME_KEY = "name"
# package.json: The name of the map file
LEVEL_MAP_FILE_KEY = "map"
# package.json: The health to provide a player for this level
LEVEL_PLAYER_HEALTH_KEY = "helath"
