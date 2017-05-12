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

		self.grid_block_height = 10
		self.grid_block_width = 10
		self.current_mouse_over_grid = None # a tuple of grid coordinates that the mouse is currently over.

		self.game_phase = "setup" # valid values: setup, battle

		self.canvas.bind("<Motion>", self.onMouseMove)
		self.reset()

	def reset(self):
		self.grid_player1 = []
		self.grid_player2 = []
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
					elif grid_space_content:
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


root = Tk()
arial14 = font.Font(family="Arial", size=14)
ubuntuMono10 = font.Font(family="Ubuntu Mono", size=10)
app = Main(root)
root.deiconify()
# app.draw()
root.mainloop()
