from cx_Freeze import setup, Executable
import sys
import resources as r
import globals as g

exe_file_name = "TakeItBack.exe"

setup(
	name=exe_file_name,
	version="1.0",
	author="Jake Thurman",
	description=r.GAME_TITLE,
	executables=[
		Executable(
			script=g.ROOT_PATH + "main.pyw",
			base="Win32GUI",
			targetName=exe_file_name,
			icon=g.ROOT_PATH + "images/logo.ico"
		)
	]
) 
