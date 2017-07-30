assignments = []

def cross(a, b):
	return [s+t for s in a for t in b]

rows = 'ABCDEFGHI'
cols = '123456789'
boxes = cross(rows, cols)

left_diag = ['A1', 'B2', 'C3', 'D4', 'E5', 'F6', 'G7', 'H8', 'I9']
right_diag = ['I1', 'H2', 'G3', 'F4', 'E5', 'D6', 'C7', 'B8', 'A9']
diagonals = [left_diag, right_diag]

row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]

unitlist = row_units + column_units + square_units + diagonals
units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s],[]))-set([s])) for s in boxes)

def loc_twins(values, unit):
	twins_list = []
	value = {}
	
	for box in unit:
		value[values[box]] = value[values[box]] + 1 if values[box] in value else 1
	for key in list(value):
		if len(key) == 2 and value[key] == 2:
			twins_list.append(key)
	if len(twins_list) > 0:
		return twins_list
	else:
		return False

def assign_value(values, box, value):
	"""
	Please use this function to update your values dictionary!
	Assigns a value to a given box. If it updates the board record it.
	"""

	# Don't waste memory appending actions that don't actually change any values
	if values[box] == value:
		return values

	values[box] = value
	if len(value) == 1:
		assignments.append(values.copy())
	return values

def naked_twins(values):
	"""Eliminate values using the naked twins strategy.
	Args:
		values(dict): a dictionary of the form {'box_name': '123456789', ...}

	Returns:
		the values dictionary with the naked twins eliminated from peers.
	"""
	# Search for instances of the naked twins
	for unit in unitlist:
		twins_list = loc_twins(values, unit)
		# Eliminate the naked twins as possibilities for their peers
		if twins_list and len(twins_list) > 0:
			for value in twins_list:
				for box in unit:
					if values[box] !=value:
						for digit in value:
							values[box] =values[box].replace(digit,'')
	return values

def grid_values(grid):
	"""Convert grid string into {<box>: <value>} dict with '123456789' value for empties.

	Args:
		grid: Sudoku grid in string form, 81 characters long
	Returns:
		Sudoku grid in dictionary form:
		- keys: Box labels, e.g. 'A1'
		- values: Value in corresponding box, e.g. '8', or '123456789' if it is empty.
	"""
	chars = []
	digits = '123456789'
	for c in grid:
		if c in digits:
			chars.append(c)
		if c == '.':
			chars.append(digits)
	assert len(chars) == 81
	return dict(zip(boxes, chars))

def display(values):
	"""
	Display the values as a 2-D grid.
	Args:
		values(dict): The sudoku in dictionary form
	"""
	width = 1+max(len(values[s]) for s in boxes)
	line = '+'.join(['-'*(width*3)]*3)
	for r in rows:
		print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
					  for c in cols))
		if r in 'CF': print(line)
	return

def eliminate(values):
	solved_values = [box for box in values.keys() if len(values[box]) ==1]
	for box in solved_values:
		digit = values[box]
		for peer in peers[box]:
			values[peer] = values[peer].replace(digit,'')
	return values

def only_choice(values):
	for unit in unitlist:
		for digit in '123456789':
			dplaces = [box for box in unit if digit in values[box]]
			if len(dplaces) == 1:
				values[dplaces[0]] = digit
				
	return values
		
def reduce_puzzle(values):
	"""
    Iterate eliminate() and only_choice(). If at some point, there is a box with no available values, return False.
    If the sudoku is solved, return the sudoku.
    If after an iteration of both functions, the sudoku remains the same, return the sudoku.
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """
	solved_values = [box for box in values.keys() if len(values[box]) == 1]
	stalled = False
	while not stalled:
		# Check how many boxes have a determined value
		solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])
		# Your code here: Use the Eliminate Strategy
		values = eliminate(values)
		# Your code here: Use the Only Choice Strategy
		values = only_choice(values)
		# Check for naked twins here
		values = naked_twins(values)
		# Check how many boxes have a determined value, to compare
		solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
		# If no new values were added, stop the loop.
		stalled = solved_values_before == solved_values_after
		# Sanity check, return False if there is a box with zero available values:
		if len([box for box in values.keys() if len(values[box]) == 0]):
			return False
	return values

def search(values):
	"Using depth-first search and propagation, try all possible values."
	# First, reduce the puzzle using the previous function
	#print(values)
	values = reduce_puzzle(values)
	if values is False:
		return False ## Failed earlier
	if all(len(values[s]) == 1 for s in boxes): 
		return values ## Solved!
	# Choose one of the unfilled squares with the fewest possibilities
	n,s = min((len(values[s]), s) for s in boxes if len(values[s]) > 1)
	# Now use recurrence to solve each one of the resulting sudokus, and 
	for value in values[s]:
		new_sudoku = values.copy()
		new_sudoku[s] = value
		attempt = search(new_sudoku)
		if attempt:
			return attempt

def solve(grid):
	"""
	Find the solution to a Sudoku grid.
	Args:
		grid(string): a string representing a sudoku grid.
			Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
	Returns:
		The dictionary representation of the final sudoku grid. False if no solution exists.
	"""
	attempt = grid_values(grid)
	return search(attempt)

if __name__ == '__main__':
	diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
	grid2 = '4.....8.5.3..........7......2.....6.....8.4......1.......6.3.7.5..2.....1.4......'
	display(solve(diag_sudoku_grid))

	try:
		from visualize import visualize_assignments
		visualize_assignments(assignments)

	except SystemExit:
		pass
	except:
		print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
