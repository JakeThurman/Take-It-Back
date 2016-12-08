
# When making somthing paginated:
#  1. Add a paging variable/PagingHandler instance
#  2. Use this calss to handle filtering
#  3. Add a {resources.NEXT_PAGE} link 'if not is_last_page()'
#  4. Don't make the user go back through all of the pages for ESC
#
class PagingHandler(object):
	def __init__(self, get_screen_size, line_height):
		self._get_screen_size = get_screen_size
		self._line_height = line_height
		
	def _get_page_index_bounds(self, page):
		lines_per_page = (self._get_screen_size()[1] / self._line_height) - 1
		
		min = (page) * lines_per_page
		max = ((page + 1) * lines_per_page) + 1
		
		return (min, max)
	
	def is_last_page(self, items, page):
		min, max = self._get_page_index_bounds(page)	
		return max >= len(items) - 1
	
	def filter_items(self, items, page):
		min, max = self._get_page_index_bounds(page)		
		return items[int(min):int(max)]

