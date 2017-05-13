#!/usr/bin/env python3
print("starting...")

# from tkinter import Frame, Canvas, Label, Button, ALL, Tk, font, BOTH
from tkinter import *
from tkinter import font
import random

random.seed(4832)
GAME_SIZE = 500 # height of the game window in pixels, width is half of this
GRID_SIZE = 10 # how many blocks each player's grid
GRID_LETTERS = [char for char in "ABCDEFGHIJ"] # y axis is labeled with letters
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
		self.selected_ship_index = None # used for boat placement

		self.canvas.bind("<Motion>", self.onMouseMove)
		self.canvas.bind("<Button-1>", self.onGridClick)
		self.canvas.bind("<Button-3>", self.onGridRightClick)
		self.canvas_placement_queue.bind("<Motion>", self.onPlacementQueueMouseMove)
		self.canvas_placement_queue.bind("<Button-1>", self.onPlacementQueueClick)
		self.reset()

	def reset(self):
		self.canvas_placement_queue.pack(fill=Y)

		self.grid_player1 = []
		self.grid_player2 = []
		self.boat_placement_queue = SHIP_LENGTHS
		for r in range(GRID_SIZE):
			self.grid_player1 += [[]]
			self.grid_player2 += [[]]
			for c in range(GRID_SIZE):
				self.grid_player1[r] += [None]
				self.grid_player2[r] += [None]

		# self.grid_player1[3][5] = "miss"
		# self.grid_player1[3][6] = "miss"
		# self.grid_player1[3][7] = "hit"
		# self.grid_player1[3][8] = "miss"
		# self.grid_player1[4][7] = "hit"
		#
		# self.grid_player2[6][1] = "miss"
		# self.grid_player2[6][2] = "hit"
		# self.grid_player2[6][3] = "hit"
		# self.grid_player2[6][4] = "hit"
		# self.grid_player2[6][5] = "miss"
		# self.grid_player2[9][6] = "miss"
		# self.grid_player2[9][7] = "miss"
		# self.grid_player2[8][9] = "miss"
		# self.grid_player2[9][9] = "miss"
		print("Game reset")

	def draw(self):
		self.canvas.delete(ALL)
		# print("GAME_SIZE: {}, GRID_SIZE: {}".format(GAME_SIZE, GRID_SIZE))
		# print("canvas size: {}".format((self.canvas.winfo_width(), self.canvas.winfo_height())))
		self.grid_block_height = int(self.canvas.winfo_height() / 2 / GRID_SIZE)
		self.grid_block_width = int(self.canvas.winfo_width() / GRID_SIZE)
		# print("grid block size: {}".format((self.grid_block_width, self.grid_block_height)))
		boat_placement, boat_placement_valid = self.getSelectedShipPlacement()
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
					if grid_space_content:
						if grid_space_content == "boat":
							circle_color = "dark gray"
					if self.current_mouse_over_grid and self.current_mouse_over_grid == grid_pos:
						if self.game_phase == "setup":
							if self.current_mouse_over_grid[0] == 1:
								circle_color = "lime green"
							else:
								circle_color = "dark red"
						elif self.game_phase == "battle":
							if self.current_mouse_over_grid[0] == 2:
								circle_color = "lime green"
							else:
								circle_color = "dark red"
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

	def draw_placement_queue(self):
		self.canvas_placement_queue.delete(ALL)
		if self.game_phase == "setup":
			# draw boat placement queue
			radius = int(QUEUE_BLOCK_SIZE / 2) - 2
			for y, boat_length in zip(range(len(self.boat_placement_queue)), self.boat_placement_queue):
				for x in range(boat_length):
					self.canvas_placement_queue.create_circle((x * QUEUE_BLOCK_SIZE) + radius + 2, (y * QUEUE_BLOCK_SIZE) + radius + 2, radius, fill="gray")

			# indicate which boat is selected
			if self.selected_ship_index != None:
				selection_width = QUEUE_BLOCK_SIZE * self.boat_placement_queue[self.selected_ship_index]
				basey = QUEUE_BLOCK_SIZE * self.selected_ship_index
				self.canvas_placement_queue.create_rectangle(0, basey, selection_width, basey + QUEUE_BLOCK_SIZE, outline="red")

	def onMouseMove(self, event):
		if self.current_mouse_over_grid != self.getGridPos(event.x, event.y):
			self.current_mouse_over_grid = self.getGridPos(event.x, event.y)
		self.draw()

	def onPlacementQueueMouseMove(self, event):
		self.draw_placement_queue()

	def onPlacementQueueClick(self, event):
		index = event.y // QUEUE_BLOCK_SIZE
		if index < len(self.boat_placement_queue):
			self.selected_ship_index = index
		else:
			self.selected_ship_index = None

		self.draw_placement_queue()

	def onGridClick(self, event):
		if self.game_phase == "setup":
			# place boat
			boat_placement, isValid = self.getSelectedShipPlacement()
			if isValid:
				for pos in boat_placement:
					self.setGridSpaceContent(*pos, "boat")
				del self.boat_placement_queue[self.selected_ship_index]
				if self.selected_ship_index >= len(self.boat_placement_queue):
					self.selected_ship_index -= 1
				if len(self.boat_placement_queue) == 0:
					self.selected_ship_index = None
					self.canvas_placement_queue.pack_forget()
					self.game_phase = "battle"
					print("Setup phase complete")
				self.draw_placement_queue()
		elif self.game_phase == "battle":
			attack_pos = self.getGridPos(event.x, event.y)
			if attack_pos[0] == 2:
				self.takeTurn(*attack_pos)
				self.aiThinkTurn()
		self.draw()

	def onGridRightClick(self, event):
		if self.game_phase == "setup":
			# rotate boat placement
			self.boat_rotation = not self.boat_rotation
		self.draw()

	def getGridPos(self, canvas_x, canvas_y):
		for p in range(MAX_PLAYERS, 0, -1):
			y_base = int(GAME_SIZE / 2 * (p - 1))
			for k in range(y_base, y_base + int(GAME_SIZE / 2), self.grid_block_height):
				for h in range(0, int(GAME_SIZE / 2) + 1, self.grid_block_width):
					if (h <= canvas_x and canvas_x <= h + self.grid_block_width) and (k <= canvas_y and canvas_y <= k + self.grid_block_height):
						return MAX_PLAYERS - p + 1, int(h / self.grid_block_width), int(k / self.grid_block_height) - ((p - 1) * GRID_SIZE)

	def setGridSpaceContent(self, player_num, grid_x, grid_y, content):
		if player_num == 1:
			self.grid_player1[grid_y][grid_x] = content
		elif player_num == 2:
			self.grid_player2[grid_y][grid_x] = content

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
			isValid = self.current_mouse_over_grid[2] + self.boat_placement_queue[self.selected_ship_index] <= GRID_SIZE
		else:
			# horizontal, y will be constant
			c = [self.current_mouse_over_grid[2]] * self.boat_placement_queue[self.selected_ship_index]
			positions = zip(range(self.current_mouse_over_grid[1], self.current_mouse_over_grid[1] + self.boat_placement_queue[self.selected_ship_index]), c)
			isValid = self.current_mouse_over_grid[1] + self.boat_placement_queue[self.selected_ship_index] <= GRID_SIZE

		positions = list(positions)
		# prepend the player numbers
		for i in range(len(positions)):
			positions[i] = (self.current_mouse_over_grid[0],) + positions[i]

		if isValid:
			for pos in positions:
				if self.getGridSpaceContent(*pos) != None:
					isValid = False

		return positions, self.current_mouse_over_grid[0] == 1 and isValid

	def takeTurn(self, player_num, grid_x, grid_y):
		if not self.getGridSpaceContent(player_num, grid_x, grid_y) == None and not self.getGridSpaceContent(player_num, grid_x, grid_y) == "boat":
			return

		attacking_player = None
		if player_num == 1:
			attacking_player = 2
		elif player_num == 2:
			attacking_player = 1
		content = None
		if self.getGridSpaceContent(player_num, grid_x, grid_y) == "boat":
			content = "hit"
		else:
			content = "miss"
		self.setGridSpaceContent(player_num, grid_x, grid_y, content)
		print("Player {} {} Player {} at {}{}".format(attacking_player, content, player_num, GRID_LETTERS[grid_y], grid_x))

	def aiThinkTurn(self):
		def _getAdjacent(grid_x, grid_y):
			adjacent = [
				(1, grid_x - 1, grid_y),
				(1, grid_x, grid_y - 1),
				(1, grid_x + 1, grid_y),
				(1, grid_x, grid_y + 1),
			]
			to_remove = []
			for i in range(len(adjacent)):
				if adjacent[i][1] < 0 or adjacent[i][1] >= GRID_SIZE or adjacent[i][2] < 0 or adjacent[i][2] >= GRID_SIZE:
					to_remove += [i]
			to_remove = sorted(to_remove, reverse=True)
			for index in to_remove:
				del adjacent[index]
			return adjacent

		# look for hits, then attack any places around them if available
		for y in range(len(self.grid_player1)):
			for x in range(len(self.grid_player1[y])):
				if self.getGridSpaceContent(1, x, y) == "hit":
					adjacent = _getAdjacent(x, y)
					for pos in adjacent:
						if self.getGridSpaceContent(*pos) not in ["hit", "miss"]:
							self.takeTurn(*pos)
							return

		# attack in a grid pattern to search for ships
		for y in range(len(self.grid_player1)):
			for x in range(len(self.grid_player1[y])):
				if y % 2 == x % 2 and self.getGridSpaceContent(1, x, y) not in ["hit", "miss"]:
					self.takeTurn(1, x, y)
					return

root = Tk()
arial14 = font.Font(family="Arial", size=14)
ubuntuMono10 = font.Font(family="Ubuntu Mono", size=10)
app = Main(root)
root.deiconify()
# app.draw()
root.mainloop()
