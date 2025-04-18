from tkinter import Tk, BOTH, Canvas
from dataclasses import dataclass, field
from typing import List, Optional
import time
import random

@dataclass
class Point:
    x: int = 0
    y: int = 0

@dataclass
class Line:
    pta: Point
    ptb: Point

    def draw(self, canvas: Canvas, fill_color: str = "black"):
        # print(f"Drawing line from ({self.pta.x}, {self.pta.y}) to ({self.ptb.x}, {self.ptb.y})")
        # print(f"Canvas: {canvas}")
        try:
            canvas.create_line(self.pta.x, self.pta.y, self.ptb.x, self.ptb.y, fill=fill_color, width=2)
        except Exception as e:
            print(f"Error: {e}")

class Window:
    def __init__(self, width: int, height: int):
        print(f"Creating new window instance {width} wide and {height} high.")
        self.root_widget = Tk()
        self.root_widget.title("Rooty Tooty")
        self.canvas_widget = Canvas(self.root_widget, width=width, height=height)
        self.canvas_widget.configure(bg = "#d9d9d9")
        self.canvas_widget.pack()
        self.window_running = False
        self.root_widget.protocol("WM_DELETE_WINDOW", self.close)

    def redraw(self):
        self.root_widget.update_idletasks()
        self.root_widget.update()

    def wait_for_close(self):
        self.window_running = True
        while self.window_running:
            self.redraw()

    def close(self):
        self.window_running = False

    def draw_line(self, line: Line, fill_color: str = "black"):
        line.draw(self.canvas_widget, fill_color=fill_color)

@dataclass
class Cell:
    has_left_wall: bool = True
    has_right_wall: bool = True
    has_top_wall: bool = True
    has_bottom_wall: bool = True
    visited: bool = False
    _x1: int = 0
    _x2: int = 0
    _y1: int = 0
    _y2: int = 0
    _win: Window = None

    def draw(self):

        left_color = "#d9d9d9" if not self.has_left_wall else "black"
        right_color = "#d9d9d9" if not self.has_right_wall else "black"
        top_color = "#d9d9d9" if not self.has_top_wall else "black"
        bottom_color = "#d9d9d9" if not self.has_bottom_wall else "black"

        # draw left wall
        line = Line(Point(self._x1, self._y1), Point(self._x1, self._y2))
        line.draw(self._win.canvas_widget, left_color)
        # draw right wall
        line = Line(Point(self._x2, self._y1), Point(self._x2, self._y2))
        line.draw(self._win.canvas_widget, right_color)
        # draw top wall
        line = Line(Point(self._x1, self._y1), Point(self._x2, self._y1))
        line.draw(self._win.canvas_widget, top_color)
        # draw bottom wall
        line = Line(Point(self._x1, self._y2), Point(self._x2, self._y2))
        line.draw(self._win.canvas_widget, bottom_color)

    def draw_move(self, to_cell, undo: bool = False):
        if undo:
            line_color = "gray"
        else:
            line_color = "red"
        my_center = Point((self._x1 + self._x2)/2, (self._y1 + self._y2)/2)
        his_center = Point((to_cell._x1 + to_cell._x2)/2, (to_cell._y1 + to_cell._y2)/2)
        path_line = Line(my_center, his_center)
        path_line.draw(self._win.canvas_widget, line_color)

@dataclass
class Maze:
    x1: int = 0
    y1: int = 0
    num_rows: int = 10
    num_cols: int = 10
    cell_size_x: int = 50
    cell_size_y: int = 50
    win: Window = None
    seed: int = None
    _cells: List[List['Cell']] = field(default_factory = list)

    def __post_init__(self):  
        if self.seed is None:
            random.seed(time.time())   
        else:
            random.seed(self.seed)       
        self._create_cells()
        self._break_entrance_and_exit()
        self._break_walls(0,0)
        self._reset_cells_visited()

    def _create_cells(self):
        for row in range(self.num_rows):
            y = self.y1 + row * self.cell_size_y
            self._cells.append([]) # add an empty row
            for col in range(self.num_cols):
                x = self.x1 + col * self.cell_size_x
                #new_cell = Cell(1,1,1,1,x,x+self.cell_size_x,y,y+self.cell_size_y,self.win)
                new_cell = Cell()
                self._cells[row].append(new_cell)
                self._draw_cell(row, col)

    def _draw_cell(self, row: int, col: int):
        this_cell = self._cells[row][col]
        this_cell._x1 = self.x1 + col * self.cell_size_x
        this_cell._y1 = self.y1 + row * self.cell_size_y
        this_cell._x2 = this_cell._x1 + self.cell_size_x
        this_cell._y2 = this_cell._y1 + self.cell_size_y
        this_cell._win = self.win
        print(f"Drawing new cell at position ({this_cell._x1}, {this_cell._y1})")
        this_cell.draw()
        self._animate(0.001)

    def _break_entrance_and_exit(self):
        last_col = self.num_cols - 1
        last_row = self.num_rows - 1
        top_left = self._cells[0][0]
        bottom_right = self._cells[last_row][last_col]
        top_left.has_left_wall = False
        bottom_right.has_bottom_wall = False
        self._draw_cell(0,0)
        self._draw_cell(last_row, last_col)

    def _find_neighbors(self, row, col):
        if col > 0:
            left = self._cells[row][col-1]
        else:
            left = None
        if col < len(self._cells[row])-1:
            right = self._cells[row][col+1]
        else:
            right = None
        if row > 0:
            up = self._cells[row-1][col]
        else:
            up = None
        if row < len(self._cells)-1:
            down = self._cells[row+1][col]
        else:
            down = None
        return left, right, up, down

    def _break_walls(self, row, col):
        this_cell = self._cells[row][col]
        this_cell.visited = True
        print(f"Checking out cell: {this_cell}")
        while True:
            to_visit = []
            # find all cell neighbors
            left, right, up, down = self._find_neighbors(row, col)

            # see which neighbors we've visited
            if left is not None and not left.visited:
                to_visit.append(left)
            if right is not None and not right.visited:
                to_visit.append(right)
            if up is not None and not up.visited:
                to_visit.append(up)
            if down is not None and not down.visited:
                to_visit.append(down)

            # if we've visited every cell, then draw this cell and break the loop
            if len(to_visit) < 1:
                self._draw_cell(row, col)
                return
            else:
                # pick a random index in the to_visit list
                # next_cell_index = random.randrange(len(to_visit))
                # next_cell = to_visit[next_cell_index]

                next_cell = random.choice(to_visit)
                # break the walls between this wall and the next
                if next_cell == left:
                    this_cell.has_left_wall = False
                    next_cell.has_right_wall = False
                    next_row = row
                    next_col = col-1
                elif next_cell == right:
                    this_cell.has_right_wall = False
                    next_cell.has_left_wall = False
                    next_row = row
                    next_col = col + 1
                elif next_cell == up:
                    this_cell.has_top_wall = False
                    next_cell.has_bottom_wall = False
                    next_row = row - 1
                    next_col = col
                elif next_cell == down:
                    this_cell.has_bottom_wall = False
                    next_cell.has_top_wall = False
                    next_row = row + 1
                    next_col = col
                self._break_walls(next_row,next_col)

    def _reset_cells_visited(self):
        for row in range(len(self._cells)):
            for col in range(len(self._cells[row])):
                self._cells[row][col].visited = False

    def _animate(self, delay):
        self.win.redraw()
        time.sleep(delay)

    def solve(self):
        return self._solve_r(0,0)
    
    def _solve_r(self, row, col):
        assert row >= 0 and row < len(self._cells), f"Row {row} out of limits"
        assert col >= 0 and col < len(self._cells[row]), f"Col {col} out of limits"

        end_cell = self._cells[len(self._cells)-1][len(self._cells[0])-1]
        this_cell = self._cells[row][col]

        self._animate(0.1)
        this_cell.visited = True

        if this_cell == end_cell:
            return True
        
        left, right, up, down = self._find_neighbors(row, col)

        #we'll always try to push down and right
        if right is not None:
            print(f"Looks like there's a cell to the right: {right}")
            if not right.has_left_wall and not this_cell.has_right_wall:
                print("... and there's not a wall in the way")
                if not right.visited:
                    print("... and it hasn't been visited")
                    this_cell.draw_move(right)
                    if self._solve_r(row, col+1):
                        return True
                    else:
                        this_cell.draw_move(right, undo=True)
        if down is not None:
            print(f"Looks like there's a cell below: {down}")
            if not down.has_top_wall and not this_cell.has_bottom_wall:
                print("... and there's not a wall in the way")
                if not down.visited:
                    print("... and it hasn't been visited")
                    this_cell.draw_move(down)
                    if self._solve_r(row+1, col):
                        return True
                    else:
                        this_cell.draw_move(down, undo=True)
        if left is not None:
            print(f"Looks like there's a cell to the left: {left}")
            if not left.has_right_wall and not this_cell.has_left_wall:
                print("... and there's not a wall in the way")
                if not left.visited:
                    print("... and it hasn't been visited")
                    this_cell.draw_move(left)
                    if self._solve_r(row, col-1):
                        return True
                    else:
                        this_cell.draw_move(left, undo=True)
        if up is not None:
            print(f"Looks like there's a cell above: {up}")
            if not up.has_bottom_wall and not this_cell.has_top_wall:
                print("... and there's not a wall in the way")
                if not up.visited:
                    print("... and it hasn't been visited")
                    this_cell.draw_move(up)
                    if self._solve_r(row-1, col):
                        return True
                    else:
                        this_cell.draw_move(up, undo=True)
        return False