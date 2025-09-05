# Edit dominos to have pairs of pips on the dominos
# Edit blank_board to be a list of rows in a rectangular format, with cells that can be filled being represented by a -1, and cells that are not fillable represented by any non-integer (such as "_")
# Edit checks to have key-value pairs, with keys being the list of indices in the grid in flattened row-major order (e.g. for a 10 wide by 13 tall grid, the 3rd element in the 4th row is (4-1)*10 + (3-1) = 32), and the value being a function that takes a list and returns True if it matches the constraint given in the puzzle

# Values below filled in for Pips #18 Hard

from collections import Counter
import math

blank_board = tuple(tuple(-1 for i in range(4)) for j in range(5))
dominos = [(1,4),(3,4),(5,3),(0,1),(5,1),(0,3),(0,5),(2,5),(4,0),(2,4)]
checks = {(0,4,5,6,7):lambda x:sum(x)==24, (1,):lambda x:sum(x)>1, (2,):lambda x:sum(x)==0, (8,12,16):lambda x:sum(x)==4, (9,10):lambda x:x[0]==x[1], (13,14,15):lambda x:(x[0] == x[1]) and (x[1] == x[2]), (17,18):lambda x:x[0]==x[1]}
solutions = []
board_w = len(blank_board[0])
board_h = len(blank_board)

def create_arrangement(state):
	board = [[i for i in j] for j in blank_board]
	for pos in state:
		temp = sum(board, start=[]).index(-1)
		y = temp//board_w
		x = temp%board_w
		if pos % 2 == 0:
			if x+1 == board_w or board[y][x+1] != -1:
				return False
		else:
			if y+1 == board_h:
				return False
		board[y][x] = 1
		board[y+1 if pos%2 else y][x+1 if pos%2==0 else x] = 1
	return True

domino_counts = Counter([tuple(sorted(i)) for i in dominos])
arrangements = sum([create_arrangement([int(i) for i in bin(2**len(dominos)+x)[3:]]) for x in range(2**len(dominos))])
orders = math.factorial(len(dominos))/math.prod([math.factorial(j) for _, j in domino_counts.items()])
print("There are", arrangements, "different ways to arrange dominos in this grid, giving a total of", int(arrangements*orders*(2**len([d for d in dominos if d[0] != d[1]]))), "possible attempted solutions.")

def eval_state(state, dominos, checks, verbose=False):
	board = [[i for i in j] for j in blank_board]
	for dom, pos in state:
		temp = sum(board, start=[]).index(-1)
		y = temp//board_w 
		x = temp%board_w 
		if pos % 2 == 0:
			if x+1 == board_w or board[y][x+1] != -1:
				if verbose: print("Failed placing domino", dom, "at", x, ",", y)
				return False
		else:
			if y+1 == board_h:
				if verbose: print("Failed placing domino", dom, "at", x, ",", y)
				return False
		board[y][x] = dominos[dom][1 if pos>= 2 else 0]
		board[y+1 if pos%2 else y][x+1 if pos%2==0 else x] = dominos[dom][0 if pos>=2 else 1]
	if verbose: print(board)
	board = sum(board, start=[])
	for indices, check in checks.items():
		subboard = [board[i] for i in indices]
		if -1 in subboard: continue
		if not check(subboard):
			if verbose: print("Failed check with indices", indices)
			return False
	return True

def solve(base_state):
	indices_used = [i[0] for i in base_state]
	indices_remaining = [i for i in range(len(dominos)) if i not in indices_used]
	if len(indices_remaining) == 0:
		solutions.append(base_state)
	for i in indices_remaining:
		for p in [0,1,2,3]:
			if eval_state(base_state+[(i,p)], dominos, checks):
				solve(base_state+[(i,p)])

def create_board(state, dominos):
	board = [[i for i in j] for j in blank_board]
	for dom, pos in state:
		temp = sum(board, start=[]).index(-1)
		y = temp//board_w 
		x = temp%board_w 
		if pos % 2 == 0:
			if x+1 == board_w or board[y][x+1] != -1:
				return False
		else:
			if y+1 == board_h:
				return False
		board[y][x] = dominos[dom][1 if pos>= 2 else 0]
		board[y+1 if pos%2 else y][x+1 if pos%2==0 else x] = dominos[dom][0 if pos>=2 else 1]
	return "\n".join(str(x) for x in board)

solve([])

print(len(solutions), "solutions found.")

with open("./output.txt", "w") as f:
	f.write("Dominos: "+str(dominos)+"\n")
	for n, solution in enumerate(solutions):
		f.write("Solution "+str(n)+":"+str(solution)+"\n")
		f.write(create_board(solution, dominos))
		f.write("\n\n")
