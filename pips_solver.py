# Usage: python pips_solver.py [date in YYYY-MM-DD format, default is today] [difficulty: "easy", "medium", or "hard", default is hard]

from collections import Counter
import math
import sys
import time
import requests
import datetime

blank_board = tuple()
dominos = []
checks = {}
solutions = []
board_w = 0
board_h = 0

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


if __name__ == "__main__":
	difficulty = "hard"
	potential_args = sys.argv[1:]
	if "easy" in potential_args :
		difficulty = "easy"
	if "medium" in potential_args :
		difficulty = "medium"
	if len([i for i in potential_args if "-" in i]) > 0:
		date = [i for i in potential_args if "-" in i][0]
	else:
		date = datetime.datetime.now().strftime("%Y-%m-%d")
	if len(date) != 10 or date[4] != "-" or date[7] != "-" or not (date[0:4]+date[5:7]+date[8:10]).isdigit():
		raise ValueError("Date must be in YYYY-MM-DD format!")
	json_data = requests.get("https://www.nytimes.com/svc/pips/v1/"+date+".json").json()[difficulty]
	
	print("Solving the", difficulty, "Pips game for the date", date)
	
	board_w = max([p[1] for d in json_data["solution"] for p in d])+1
	board_h = max([p[0] for d in json_data["solution"] for p in d])+1
	
	blank_board = tuple(tuple(-1 for i in range(board_w)) for j in range(board_h))
	dominos = [tuple(i) for i in json_data["dominoes"]]
	constrainer = {"sum": (lambda y: (lambda z:sum(z)==y)), "equals": lambda y:(lambda z:z.count(z[0]) == len(z)), "unequal": lambda y:(lambda z:len(set(z))==len(z)), "greater": (lambda y: (lambda z:sum(z)>y)), "less": (lambda y: (lambda z:sum(z)<y))}
	checks = {tuple(i[0]*board_w+i[1] for i in r["indices"]):constrainer[r["type"]](r["target"] if "target" in r else 0) for r in json_data["regions"] if r["type"] != "empty"}
	solutions = []

	domino_counts = Counter([tuple(sorted(i)) for i in dominos])
	arrangements = sum([create_arrangement([int(i) for i in bin(2**len(dominos)+x)[3:]]) for x in range(2**len(dominos))])
	orders = math.factorial(len(dominos))/math.prod([math.factorial(j) for _, j in domino_counts.items()])
	print("There are", arrangements, "different ways to arrange dominos in this grid, giving a total of", int(arrangements*orders*(2**len([d for d in dominos if d[0] != d[1]]))), "possible attempted solutions.")

	start = time.time()
	solve([])

	print(len(solutions), "solutions found.")
	print("Took", time.time()-start, "seconds to find all solutions.")

	with open("./output.txt", "w") as f:
		f.write("Dominos: "+str(dominos)+"\n")
		for n, solution in enumerate(solutions):
			f.write("Solution "+str(n)+":"+str(solution)+"\n")
			f.write(create_board(solution, dominos))
			f.write("\n\n")
