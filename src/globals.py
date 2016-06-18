""" Game 'globals', but globals are generally bad, 
	so we're using this constants file for that.
	Don't add to this list unless absolutely needed.
"""
import os
def __parent(p):
    return os.path.normpath(os.path.join(p, os.path.pardir)) + "\\"

ROOT_PATH = __parent(__file__)
if ".zip" in ROOT_PATH:
	ROOT_PATH = __parent(ROOT_PATH)

APP_DATA_PATH = os.path.expanduser('~') + "/AppData/Roaming/Take It Back/"
