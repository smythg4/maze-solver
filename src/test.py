import unittest
from maze import Maze, Window

class Tests(unittest.TestCase):
    def test_maze_create_cells(self):
        num_cols = 12
        num_rows = 10
        m1 = Maze(5,5,num_rows, num_cols, 10, 10, Window(800,600))
        self.assertEqual(len(m1._cells), num_rows)
        self.assertEqual(len(m1._cells[0]), num_cols)

    def test_ent_exit(self):
        num_cols = 12
        num_rows = 10
        m1 = Maze(5,5,num_rows, num_cols, 50, 50, Window(800,600))
        m1._break_entrance_and_exit()
        self.assertEqual(m1._cells[0][0].has_left_wall, False)
        self.assertEqual(m1._cells[num_rows-1][num_cols-1].has_bottom_wall, False)

    def test_break_walls(self):
        num_cols = 15
        num_rows = 10
        m1 = Maze(5,5,num_rows, num_cols, 50, 50, Window(800,600))
        m1._break_entrance_and_exit()
        m1.seed = 3
        m1._break_walls(0,0)
        m1._reset_cells_visited()
        self.assertEqual(m1._cells[0][0].visited,False)
        self.assertEqual(m1._cells[1][0].visited,False)
        self.assertEqual(m1._cells[0][1].visited,False)
        self.assertEqual(m1._cells[1][1].visited,False)

if __name__ == "__main__":
    unittest.main()