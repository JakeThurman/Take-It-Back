# Changed to definition based on response by StackOverflow user "Paul Draper"
# src: http://stackoverflow.com/questions/20677795/how-do-i-compute-the-intersection-point-of-two-lines-in-python
def line_seg_intersect(line1, line2):
    xdiff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
    ydiff = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1])

    def det(a, b):
        return a[0] * b[1] - a[1] * b[0]
	
    return det(xdiff, ydiff) == 0
	
(CANT_SEE, LEFT, RIGHT) = range(3)

def get_direction(source, target, blocking_items):
    if not can_see(source, target, blocking_items):
        return CANT_SEE

    return RIGHT if source.rect.center[0] > target.rect.center[0] else LEFT

def can_see(source, target, blocking_items):
    """
		Performs a los check from the center of the source to the center of the target.
		Makes the following assumtion:
			1 - Both the source and target are objects that include a pygame.Rect() member object
				called object.rect.

		Returns 1 of line of sight is clear. Returns 0 if it is blocked.
    """
    line1 = (source.rect.center, target.rect.center)
 
    # Check each candidate rect against this los line. If any of them intersect, the los is blocked.
    for item in blocking_items:
        if item != target and item != source and (line_seg_intersect(line1, (item.rect.topleft, item.rect.bottomright)) or line_seg_intersect(line1, (item.rect.topright, item.rect.bottomleft))):
            return False
	
    return True