import random

class Cell(object):
	def __init__(self, location):
		self._location = location
		
	def get_location(self):
		return self._location

class Wall(Cell):		
	def __str__(self):
		return "X"

class Air(Cell):
	def __str__(self):
		return " "

class OpenSide(object):
	LEFT = 0
	RIGHT = 1
	TOP = 2
	BOTTOM = 3
		
class Room(object):
	def __init__(self, location, height, width):
		self._location = location
		self._height = height
		self._width = width
		self.cells = list((list((self._get_item(x, y) for x in range(width))) for y in range(height)))
		
	def _get_item(self, x, y):
		return Wall((x, y))
		
	def get_location(self):
		return self._location
		
	def get_all_points(self):
		for x in range(self._width):
			for y in range(self._height):
				yield (x, y)
				
	def make_air(self, point):
		x, y = point
		self.cells[x][y] = Air(point)
	
	def has_point(self, point):
		x, y = point
		return x >= 0 and y >= 0 and x < self._width and y < self._height
				
	def __str__(self):
		return "Room @{0}".format(self.get_location())

class EmptyRoom(Room):
	def _get_item(self, x, y):
		return Air((x, y))
		
class World(object):
	def __init__(self, height, width):
		self._height = height
		self._width = width
		self.rooms = list((list((None for __ in range(height))) for _ in range(width)))
		self.ordered_rooms = []
	
	def get_dimensions(self):
		return(self._width, self._height)
	
	def init_at(self, point, rm):
		x, y = point
		self.rooms[x][y] = rm
		self.ordered_rooms.append(rm)
		
	def has_point(self, point):
		x, y = point
		return x >= 0 and y >= 0 and x < self._width and y < self._height
		
	def fill_empty_spaces(self, room_height, room_width):
		for x in range(self._width):
			for y in range(self._height):
				if self.rooms[x][y] == None:
					self.rooms[x][y] = EmptyRoom((x, y), room_height, room_width)
			
		
class PathFinder(object):
	def _should_take(self, taken, point, end_point, remaining_distance, is_valid):		
		# If this is the end, and we're not ready for that. Don't do that.
		if remaining_distance > 0 and point == end_point:
			return False
		
		return point not in taken and is_valid(point)

	def find_any_path(self, curr_point, end_point, min_distance, action, is_valid, taken=[]):
		# Mark this location
		action(curr_point)
		taken.append(curr_point)
		
		# See if we found the end
		if (curr_point == end_point and min_distance <= 0):
			return True
		
		# Dig deeper!		
		remaining_distance = min_distance - 1

		new_x_y_options = list(filter(lambda point: self._should_take(taken, point, remaining_distance, end_point, is_valid), [
			(curr_point[0] + 1, curr_point[1]), # North
			(curr_point[0], curr_point[1] + 1), # East
			(curr_point[0] - 1, curr_point[1]), # South
			(curr_point[0], curr_point[1] - 1)  # West
		]))
		
		if len(new_x_y_options) == 0:
			return False
		
		new_point = random.choice(new_x_y_options)
		return self.find_any_path(new_point, end_point, remaining_distance, action, is_valid, taken)
		
class RoomFiller(object):
	def __init__(self, path_finder):
		self._path_finder = path_finder

	def make_rooms(self, world, start_point, end_point, min_distance, room_height, room_width):
		action = lambda point: world.init_at(point, Room(point, room_height, room_width))
		return self._path_finder.find_any_path(start_point, end_point, min_distance, action, is_valid=world.has_point)		
	
	def add_air_to_room(self, room, start_point, end_point, min_distance):
		#TODO: Fix this method. It almost always fails.
		validator = RoomExcavationValidator(start_point, room.has_point)
		
		action = Utils.combine_funcs(room.make_air, validator.mark_point)
		
		return self._path_finder.find_any_path(start_point, end_point, min_distance, action, is_valid=validator.is_valid_cut)	

class RoomExcavationValidator(object):
	def __init__(self, start_point, is_otherwise_valid):
		self._last_point = start_point
		self._is_otherwise_valid = is_otherwise_valid
		self._last_movement_was_up = False
		self._prev_last_mvmt_was_up = False
	
	def mark_point(self, point):
		# Update the "last" variables for the next call
		self._prev_last_mvmt_was_up = self._last_movement_was_up
		self._last_movement_was_up = self._last_point[1] < point[1]
		self._last_point = point
	
	def is_valid_cut(self, point):
		# Just return false now if the other checks fail
		if not self._is_otherwise_valid(point):
			return False
		
		# Don't let the pathfinder go upwards more than twice!!
		would_be_3_ups = self._prev_last_mvmt_was_up and self._last_movement_was_up and self._last_point[1] < point[1]
				
		return not would_be_3_ups
	
class Utils(object):
	@staticmethod
	def windowed(lst):
		for i in range(1, len(lst) - 1):
			curr = lst[i - 1]
			next = lst[i]
			yield (curr, next)
			
	@staticmethod
	def map2D(func, list_2d):
		return map(lambda items: map(func, items), list_2d)
	
	@staticmethod
	def convert2Dtostr(list_2d):	
		stringified_items = Utils.map2D(str, list_2d)
		
		return '\n'.join(map(lambda lst: ''.join(lst), stringified_items))
		
	@staticmethod
	def combine_funcs(*funcs):
		def action(*args, **kwargs):
			for func in funcs:
				func(*args, **kwargs)
		
		return action
		
	@staticmethod	
	def joing_strings_horizontally(left, right):
		zipped = zip(left.splitlines(), right.splitlines())
		mapped = map("".join, zipped)
		return '\n'.join(mapped)
	
class WorldGenerator(object):
	def __init__(self, room_filler, error_handler):
		self._room_filler = room_filler
		self._error_handler = error_handler
	
	def _get_actions(self, world):
			room_height=10
			room_width=10
	
			yield ("Make Rooms", lambda: self._room_filler.make_rooms(world, start_point=(3, 3), end_point=(5, 5), min_distance=4, room_height=room_height, room_width=room_width))
			
			for room in world.ordered_rooms:
				name = "Excavate Room @{0}".format(room.get_location())
				yield (name, lambda: self._room_filler.add_air_to_room(room, start_point=(5, 0), end_point=(5, 9), min_distance=4))
				
			yield ("Fill empty space on Map with blank rooms", lambda: world.fill_empty_spaces(room_height, room_width))
		
	def generate(self, continue_on_error=False):
		my_world = World(8, 8)
				
		for name, action in self._get_actions(my_world):
			success = action() != False
			if not success:
				self._error_handler.handle_failed_map_gen_action(name)
				if not continue_on_error:
					return
			else:
				print("Successfully handled action: {0}".format(name))
				
		return my_world
		
class ErrorHandler(object):
	def handle_failed_map_gen_action(self, failed_action_name):
		print('Failed on attempt to execure action: "{0}"'.format(failed_action_name))
		
class WorldConverter(object):
	def to_map_file_content(self, world):
		rooms = Utils.map2D(lambda room: Utils.convert2Dtostr(room.cells), world.rooms)
		
		rows = self._get_row_strings(world, rooms)
		
		return "\n".join(rows)
	
	def _get_row_strings(self, world, rooms):
		num_cols, num_rows = world.get_dimensions()

		for y in range(num_rows):
			curr_row = ""
		
			for x in range(num_cols):
				if curr_row == "":
					curr_row = rooms[x][y]
				
				curr_row = Utils.joing_strings_horizontally(curr_row, rooms[x][y])
				
			yield curr_row
		
		
class FileWritter(object):
	def write_to_file(self, content, file_path):
		with open(file_path, "w") as text_file:
			text_file.write(content)
		
class Program(object):
	def __init__(self):
		self._world_gen = WorldGenerator(RoomFiller(PathFinder()), ErrorHandler())
		self._world_converter = WorldConverter()
		self._file_writter = FileWritter()

	def main(self):
		my_world = self._world_gen.generate(continue_on_error=True)
	
		if my_world != None:
			content = self._world_converter.to_map_file_content(my_world)
			self._file_writter.write_to_file(content, "output.map")
			
			
if __name__ == "__main__":
	Program().main()
	