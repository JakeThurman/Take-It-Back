"""Manages the settings of the game
"""

import json, resources

class Keys:
	"""JSON data file keys constants needed by the game
	"""

	"""LEVEL FILES"""
	# The folder where levels are stored
	LEVELS_PREFIX = "levels/"
	# The path to the data file
	JSON_DATA_FILE_NAME = "levels/data.json"
	# The name of a package
	PACKAGE_JSON_FILE_NAME = "/package.json"

	"""JSON KEYS"""
	# data.json: The levels the user has unlocked
	UNLOCKED_LEVELS_KEY = "unlocked"
	
	# data.json: The json key for completed items
	COMPLETED_LEVELS_KEY = "completed"
	# data.json: The total rings for a completed level
	COMPLETED_LEVEL_TOTAL_RINGS_KEY = "total-rings"
	# data.json: The rings found for a completed level
	COMPLETED_LEVEL_MY_RINGS_KEY = "rings"
	# data.json: The rings found for a completed level
	COMPLETED_LEVEL_MY_HEALTH_KEY = "health"	
	
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
	# package.json: The levels (by map file name) that this level unlocks
	LEVEL_UNLOCKS_KEY = "unlocks"
	# package.json: Is this level locked by default?
	LEVEL_LOCKED_KEY = "locked"
	
	# data.json: The json key for the settings object
	SETTINGS_KEY = "settings"
	# data.json: The json key for the jump key settings
	SETTING_JUMP_KEY = "jump"
	# data.json: The json key for the crouch key settings
	SETTING_CROUCH_KEY = "crouch"
	# data.json: The json key for the move left key settings
	SETTING_LEFT_KEY = "left"
	# data.json: The json key for the move right key settings
	SETTING_RIGHT_KEY = "right"

# Loads the JSON once. Effectivly a singleton because it is in the root of the module
with open(Keys.JSON_DATA_FILE_NAME, "r") as data_file:    
	_json_data = json.load(data_file)
	
def perform_update(action):
	"""@action is a function that takes the current state of the json
	and mutates it (unfortunatly). The function should return a 
	boolean flag as to if it made any changes. If True is returned
	the JSON will be stored in the source file.		
	"""
	
	# Run the update action and check the "made change" flag returned
	if action(_json_data):
		# Update the data file with new data
		with open(Keys.JSON_DATA_FILE_NAME, 'w') as outfile:
			json.dump(_json_data, outfile, indent=2)
			
def use_json(func):
	"""Allows the entire JSON object to be used inside of a function
	"""
	return func(_json_data)

# Used specificly in the settings screen but it made the most sense to put as a part of the manager to keep it together
_user_settings_text = {
	Keys.SETTING_JUMP_KEY: resources.JUMP_KEY_NAME,
	Keys.SETTING_CROUCH_KEY: resources.CROUCH_KEY_NAME,
	Keys.SETTING_LEFT_KEY: resources.MOVE_LEFT_KEY_NAME,
	Keys.SETTING_RIGHT_KEY: resources.MOVE_RIGHT_KEY_NAME
}

def get_user_settings():
	"""Generates a "list" of Tuples: <key, title, value> for each of the keys in _user_settings_text
	"""
	for key in _user_settings_text.keys():
		yield (key, _user_settings_text[key], _json_data[Keys.SETTINGS_KEY][key])
		
def get_user_setting( key):
	"""Gets the value of a single setting with key of @key
	"""
	return _json_data[Keys.SETTINGS_KEY][key]

def update_user_setting(key, value):
	"""Us
	"""
	def update(json):
		json[Keys.SETTINGS_KEY][key] = value
		return True
	
	perform_update(update)