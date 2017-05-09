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

		self.grid_block_height = 10
		self.grid_block_width = 10
		self.current_mouse_over_grid = None # a tuple of grid coordinates that the mouse is currently over.

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

		print("Game reset")

	def draw(self):
		self.canvas.delete(ALL)
		# print("GAME_SIZE: {}, GRID_SIZE: {}".format(GAME_SIZE, GRID_SIZE))
		# print("canvas size: {}".format((self.canvas.winfo_width(), self.canvas.winfo_height())))
		self.grid_block_height = int(self.canvas.winfo_height() / 2 / GRID_SIZE)
		self.grid_block_width = int(self.canvas.winfo_width() / GRID_SIZE)
		# print("grid block size: {}".format((self.grid_block_width, self.grid_block_height)))
		for p in range(MAX_PLAYERS, 0, -1):
			for y in range(0, int(GAME_SIZE / 2 * p), self.grid_block_height):
				# for x in range(int(GAME_SIZE * .25), int(GAME_SIZE * .75), self.grid_block_width):
				for x in range(0, int(GAME_SIZE / 2), self.grid_block_width):
					# print("placing grid block {}".format((x, y, x + self.grid_block_width, y + self.grid_block_height)))
					self.canvas.create_rectangle(x, y, x + self.grid_block_width, y + self.grid_block_height)

					grid_pos = self.getGridPos(x, y)
					try:
						grid_space_content = self.getGridSpaceContent(*grid_pos)
					except Exception as e:
						print("cant get content at: {}".format(grid_pos))
						# print(self.grid_player2)
					circle_color = None
					if grid_space_content:
						if grid_space_content == "hit":
							circle_color = "red"
						elif grid_space_content == "miss":
							circle_color = "white"
					elif self.current_mouse_over_grid and self.current_mouse_over_grid == grid_pos:
						circle_color = "green"
					if circle_color:
						grid_center = self.getGridSpaceCenter(*grid_pos)
						radius = int(min(self.grid_block_width, self.grid_block_height) / 4)
						radius = max(3, radius)
						self.canvas.create_circle(*grid_center, radius, fill=circle_color)



	def onMouseMove(self, event):
		self.current_mouse_over_grid = self.getGridPos(event.x, event.y)
		self.draw()

	def getGridPos(self, canvas_x, canvas_y):
		for p in range(1, MAX_PLAYERS + 1, 1):
			for k in range(0, int(GAME_SIZE / 2 * p), self.grid_block_height):
				for h in range(0, int(GAME_SIZE / 2), self.grid_block_width):
					if (h <= canvas_x and canvas_x <= h + self.grid_block_width) and (k <= canvas_y and canvas_y <= k + self.grid_block_height):
						return p, int(h / self.grid_block_width), int(k / self.grid_block_height) - ((p - 1) * GRID_SIZE)

	def getGridSpaceContent(self, player_num, grid_x, grid_y):
		if player_num == 1:
			return self.grid_player1[grid_y][grid_x]
		elif player_num == 2:
			return self.grid_player2[grid_y][grid_x]

	def getGridSpaceCenter(self, player_num, grid_x, grid_y):
		_p = MAX_PLAYERS - player_num
		return grid_x * self.grid_block_width + (self.grid_block_width / 2), grid_y * self.grid_block_height * _p  + (self.grid_block_height / 2)
		# + (player_num - 1 * GRID_SIZE * self.grid_block_height)


root = Tk()
arial14 = font.Font(family="Arial", size=14)
app = Main(root)
root.deiconify()
# app.draw()
root.mainloop()
