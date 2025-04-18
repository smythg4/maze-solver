from maze import Maze, Window

def main():
    win = Window(800, 600)

    # cell1 = Cell(1,0,1,1,50,150,50,150,win)
    # cell2 = Cell(0,1,1,0,150,250,50,150,win)
    # cell3 = Cell(1,1,0,1,150,250,150,250,win)

    # cell1.draw()
    # cell2.draw()
    # cell3.draw()
    # cell1.draw_move(cell2, False)
    # cell2.draw_move(cell3, True)

    maze = Maze(5,5,22,30,25,25, win=win)
    maze.solve()

    win.wait_for_close()

if __name__ == '__main__':
    main()