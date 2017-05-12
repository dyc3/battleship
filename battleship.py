#!/usr/bin/env python3
print("starting...")

# from tkinter import Frame, Canvas, Label, Button, ALL, Tk, font, BOTH
from tkinter import *
from tkinter import font
import random

random.seed(4832)
GAME_SIZE = 500 # height of the game window in pixels, width is half of this
GRID_SIZE = 10 # how many blocks each player's grid
MAX_PLAYERS = 2
SHIP_LENGTHS = [5, 4, 3, 3, 2]
QUEUE_BLOCK_SIZE = 16

def _create_circle(self, x, y, r, **kwargs):
	return self.create_oval(x-r, y-r, x+r, y+r, **kwargs)
Canvas.create_circle = _create_circle

def _create_circle_arc(self, x, y, r, **kwargs):
	if "start" in kwargs and "end" in kwargs:
		kwargs["extent"] = kwargs["end"] - kwargs["start"]
		del kwargs["end"]
	return self.create_arc(x-r, y-r, x+r, y+r, **kwargs)
Canvas.create_circle_arc = _create_circle_arc

class Main(object):
	def __init__(self, master):
		super(Main, self).__init__()

		self.frame = Frame(master)
		self.frame.pack(fill=BOTH, expand=1)

		self.canvas = Canvas(self.frame, width=int(GAME_SIZE / 2), height=GAME_SIZE)
		self.canvas.pack(fill=BOTH, expand=1)
		self.canvas.config(highlightbackground="yellow", highlightthickness=2)
		self.canvas_placement_queue = Canvas(self.frame, width=int(GAME_SIZE / 2), height=(len(SHIP_LENGTHS) * QUEUE_BLOCK_SIZE))
		self.canvas_placement_queue.pack(fill=Y)

		self.grid_block_height = 10
		self.grid_block_width = 10
		self.current_mouse_over_grid = None # a tuple of grid coordinates that the mouse is currently over.

		self.game_phase = "setup" # valid values: setup, battle
		self.boat_rotation = False # True is vertical, False is horizontal
		self.selected_ship_index = 0 # used for boat placement

		self.canvas.bind("<Motion>", self.onMouseMove)
		self.reset()

	def reset(self):
		self.grid_player1 = []
		self.grid_player2 = []
		self.boat_placement_queue = SHIP_LENGTHS
		for r in range(GRID_SIZE):
			self.grid_player1 += [[]]
			self.grid_player2 += [[]]
			for c in range(GRID_SIZE):
				self.grid_player1[r] += [None]
				self.grid_player2[r] += [None]

		self.grid_player1[3][5] = "miss"
		self.grid_player1[3][6] = "miss"
		self.grid_player1[3][7] = "hit"
		self.grid_player1[3][8] = "miss"
		self.grid_player1[4][7] = "hit"

		self.grid_player2[6][1] = "miss"
		self.grid_player2[6][2] = "hit"
		self.grid_player2[6][3] = "hit"
		self.grid_player2[6][4] = "hit"
		self.grid_player2[6][5] = "miss"
		self.grid_player2[9][6] = "miss"
		self.grid_player2[9][7] = "miss"
		self.grid_player2[8][9] = "miss"
		self.grid_player2[9][9] = "miss"
		print("Game reset")

	def draw(self):
		self.canvas.delete(ALL)
		# print("GAME_SIZE: {}, GRID_SIZE: {}".format(GAME_SIZE, GRID_SIZE))
		# print("canvas size: {}".format((self.canvas.winfo_width(), self.canvas.winfo_height())))
		self.grid_block_height = int(self.canvas.winfo_height() / 2 / GRID_SIZE)
		self.grid_block_width = int(self.canvas.winfo_width() / GRID_SIZE)
		# print("grid block size: {}".format((self.grid_block_width, self.grid_block_height)))
		boat_placement, boat_placement_valid = self.getSelectedShipPlacement()
		print((boat_placement, boat_placement_valid))
		for p in range(MAX_PLAYERS, 0, -1):
			for y in range(int(GAME_SIZE / 2 * (p - 1)) - 1, int(GAME_SIZE / 2 * p) + 1, self.grid_block_height):
				# for x in range(int(GAME_SIZE * .25), int(GAME_SIZE * .75), self.grid_block_width):
				for x in range(0, int(GAME_SIZE / 2) + 1, self.grid_block_width):
					# print("placing grid block {}".format((x, y, x + self.grid_block_width, y + self.grid_block_height)))
					self.canvas.create_rectangle(x, y, x + self.grid_block_width, y + self.grid_block_height)

					grid_pos = self.getGridPos(x, y)
					try:
						grid_space_content = self.getGridSpaceContent(*grid_pos)
					except Exception as e:
						continue
					circle_color = None
					if self.current_mouse_over_grid and self.current_mouse_over_grid == grid_pos:
						circle_color = "lime green"
					elif self.game_phase == "setup":
						if boat_placement and grid_pos in boat_placement:
							if boat_placement_valid:
								circle_color = "light gray"
							else:
								circle_color = "dark red"
					elif self.game_phase == "battle":
						if grid_space_content:
							if grid_space_content == "hit":
								circle_color = "red"
							elif grid_space_content == "miss":
								circle_color = "white"
					if circle_color:
						grid_center = self.getGridSpaceCenter(*grid_pos)
						radius = int(min(self.grid_block_width, self.grid_block_height) / 4)
						radius = max(3, radius)
						self.canvas.create_circle(*grid_center, radius, fill=circle_color)

		# draw a thicker line in the middle between the player's boards
		self.canvas.create_line(0, int(GAME_SIZE / 2), int(GAME_SIZE / 2), int(GAME_SIZE / 2), width=3)

		if self.game_phase == "setup":
			# draw boat placement queue
			radius = int(QUEUE_BLOCK_SIZE / 2) - 2
			for y, boat_length in zip(range(len(self.boat_placement_queue)), self.boat_placement_queue):
				for x in range(boat_length):
					self.canvas_placement_queue.create_circle((x * QUEUE_BLOCK_SIZE) + radius + 2, (y * QUEUE_BLOCK_SIZE) + radius + 2, radius, fill="gray")

	def onMouseMove(self, event):
		if self.current_mouse_over_grid != self.getGridPos(event.x, event.y):
			self.current_mouse_over_grid = self.getGridPos(event.x, event.y)
		self.draw()

	def getGridPos(self, canvas_x, canvas_y):
		for p in range(MAX_PLAYERS, 0, -1):
			y_base = int(GAME_SIZE / 2 * (p - 1))
			for k in range(y_base, y_base + int(GAME_SIZE / 2), self.grid_block_height):
				for h in range(0, int(GAME_SIZE / 2) + 1, self.grid_block_width):
					if (h <= canvas_x and canvas_x <= h + self.grid_block_width) and (k <= canvas_y and canvas_y <= k + self.grid_block_height):
						return MAX_PLAYERS - p + 1, int(h / self.grid_block_width), int(k / self.grid_block_height) - ((p - 1) * GRID_SIZE)

	def getGridSpaceContent(self, player_num, grid_x, grid_y):
		if player_num == 1:
			return self.grid_player1[grid_y][grid_x]
		elif player_num == 2:
			return self.grid_player2[grid_y][grid_x]

	def getGridSpaceCenter(self, player_num, grid_x, grid_y):
		_p = MAX_PLAYERS - player_num
		base_x = grid_x * self.grid_block_width
		base_y = grid_y * self.grid_block_height + _p * (GAME_SIZE / 2)
		return int(base_x + (self.grid_block_width / 2)), int(base_y + (self.grid_block_height / 2))
		# + (player_num - 1 * GRID_SIZE * self.grid_block_height)

	def getSelectedShipPlacement(self):
		"""
		Returns a 2 tuple of an array of grid positions that hold the selected ship, starting from the position of the selector, and a boolean determining the validity of the ship placement.
		"""
		if not self.current_mouse_over_grid or self.selected_ship_index == None:
			return None, False
		if not self.boat_placement_queue or len(self.boat_placement_queue) == 0:
			return None, False

		c = []
		positions = []
		isValid = None
		if self.boat_rotation:
			# vertical, x will be constant
			c = [self.current_mouse_over_grid[1]] * self.boat_placement_queue[self.selected_ship_index]
			positions = zip(c, range(self.current_mouse_over_grid[2], self.current_mouse_over_grid[2] + self.boat_placement_queue[self.selected_ship_index]))
			isValid = self.current_mouse_over_grid[2] + self.boat_placement_queue[self.selected_ship_index] > GRID_SIZE
		else:
			# horizontal, y will be constant
			c = [self.current_mouse_over_grid[2]] * self.boat_placement_queue[self.selected_ship_index]
			positions = zip(range(self.current_mouse_over_grid[1], self.current_mouse_over_grid[1] + self.boat_placement_queue[self.selected_ship_index]), c)
			isValid = self.current_mouse_over_grid[1] + self.boat_placement_queue[self.selected_ship_index] > GRID_SIZE

		positions = list(positions)
		# prepend the player numbers
		for i in range(len(positions)):
			positions[i] = (self.current_mouse_over_grid[0],) + positions[i]

		return positions, self.current_mouse_over_grid[0] == 1 and isValid


root = Tk()
arial14 = font.Font(family="Arial", size=14)
ubuntuMono10 = font.Font(family="Ubuntu Mono", size=10)
app = Main(root)
root.deiconify()
# app.draw()
root.mainloop()
