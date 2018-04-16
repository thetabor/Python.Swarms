#! /usr/bin/env python
'''
Simple game where a Navigator attempts to route to a goal "flag"
'''

# game imports
from random import random, sample, randint
from game import BoardGame
from board import Board
from figure import Figure, FigureStrategy
from logger import log
from game_display_helper import make_gif

# utilities
import numpy as np

# Navigator game main class
class NaviGame(BoardGame):
    def __init__(self,
            height = 4,
            width = 4,
            goal = None,
            obstacles = 0,
            moving_target = False,
            goal_idle = 3,
            display_str = "NaviGame"):
        self.board = Board(height, width)
        if goal == None:
            self.goal = (int(height/2), int(width/2))
        else:
            self.goal = goal
        self.obstacle_count = obstacles
        self.board.obstacles = []
        self.moving_target = moving_target
        self.goal_idle = goal_idle
        self.display_str_base = display_str
        self.score = 0

    def setup(self, s = None):
        # setup obstacles
        for i in range(self.obstacle_count):
            obs = self.add_block()
            self.board.obstacles.append(obs)
        # setup flag
        self.Flag = Figure(self.board)
        self.Flag.bindStrategy(FlagStrategy())
        if self.goal == None:
            self.Flag.strategy.placeIt()
            self.goal = self.Flag.position()
        else:
            self.Flag.strategy.placeIt(y = self.goal[0], x = self.goal[1])
        self.Flag.color = 2
        # setup navigator
        self.Navigator = Figure(self.board)
        if s == None: s = NaviStrategy(goal = (self.goal[0], self.goal[1]))
        self.Navigator.bindStrategy(s)
        self.Navigator.strategy.placeIt()
        self.Navigator.color = 3
        _, dist_test = self.Navigator.strategy.get_input()
        if dist_test < self.board.height - 1:
            self.reset()

    def reset(self):
        self.shift_obstacles()
        self.shift_goal()
        self.shift_figure(self.Navigator)
        self.score = 0
        _, dist_test = self.Navigator.strategy.get_input()
        if dist_test < 3:
            self.reset()

    def shift_goal(self, goal = None, figure = None):
        if goal == None:
            goal = (randint(0, self.board.height-1), randint(0, self.board.width-1))
        try:
            self.goal = goal
            self.Flag.move(y = goal[0], x = goal[1], relative=False)
            if figure == None:
                self.Navigator.strategy.goal = goal
            else:
                figure.strategy.goal = goal
        except:
            self.shift_goal()

    def shift_obstacles(self):
        for obs in self.board.obstacles:
            self.shift_figure(obs)

    def shift_figure(self, figure):
        new_pos_x = randint(0, self.board.width-1)
        new_pos_y = randint(0, self.board.height-1)
        try:
            figure.move(y = new_pos_y, x = new_pos_x, relative = False)
        except:
            self.shift_figure(figure)

    def step(self):
        for figure in self.board.figures:
            figure.strategy.step()
        if (self.Navigator.strategy.at_goal > self.goal_idle) \
                        and (self.moving_target == True):
            self.shift_goal()
            self.Navigator.strategy.at_goal = 0
        if (self.Navigator.strategy.at_goal > 0):
            self.score += 1
        else:
            self.score += -1
        self.display_str = self.display_str_base + ", Score: " + "{0:.2f}".format(self.score)

    def add_block(self, position = None):
        block = Figure(self.board)
        block.bindStrategy(FlagStrategy())
        if position != None:
                block.strategy.placeIt(y = position[0], x = position[1], soft = True)
        else:
                block.strategy.placeIt(soft = True)
        block.color = -1
        return block

    def add_wall(self, start = None, length = 5, step = None):
        Wall = []
        if step == None:
            step = (0, 0)
            while step == (0, 0):
                step = (randint(-2, 2),randint(-2, 2))
        if start == None:
            xstart = randint(1, self.board.width)
            ystart = randint(1, self.board.height)
            start = (ystart, xstart)
        for i in range(length):
            pos = (start[0] + i * step[0], start[1] + i * step[1])
            if (pos[0] < self.board.height) and (pos[1] < self.board.width):
                # there is just one error here - board taken exception
                # we can skip that segment
                try:
                    Wall.append(self.add_block(pos))
                except:
                    pass
        return Wall

# flag for the target location
class FlagStrategy(FigureStrategy):
    symbol = "~"

    def placeIt(self, x=None, y=None, soft = False):
        if x == None and y == None:
            y = sample(range(0, self.board.height), 1)[0]
            x = sample(range(0, self.board.width), 1)[0]
        try:
            self.figure.add(y=y, x=x)
        except:
            if soft == False:
                self.placeIt(x=x+randint(-1, 1), y=y+randint(-1, 1))
            else:
                print("Figure position not available, figure not placed")
                pass

    def step(self):
        pass

# navigator to get to target
class NaviStrategy(FigureStrategy):
    def __init__(self, goal):
        self.symbol = "."
        self.goal = goal
        # right, left, up, down (y, x), stay
        self.actions = [(0, 1), (0, -1), (1, 0), (-1, 0), (0, 0)]
        self.at_goal = 0
        self.last_choice = 4
        self.epsilon = 0.01 # 1% defualt exploration

    def __str__(FigureStrategy):
        return "NaviStrategy"

    def placeIt(self, x=None, y=None, soft = False):
        if x == None and y == None:
            y = sample(range(0, self.board.height), 1)[0]
            x = sample(range(0, self.board.width), 1)[0]
        try:
            self.figure.add(y=y, x=x)
        except:
            if soft == False:
                self.placeIt(x=x+randint(-1, 1), y=y+randint(-1, 1))
            else:
                print("Figure position not available, figure not placed")
                pass

    def get_input(self, position = None, pixel_ipt = False):
        if position == None:
            position = list(self.figure.position())
        goal = self.goal
        dist = self.get_distance(position, goal)
        if pixel_ipt == True:
            s = np.array(self.board.cells)
            color = lambda i: 0 if i == None else i.color
            colormask = np.vectorize(color)
            ipt = colormask(s)
            # n = self.board.width * self.board.height
        else:
            # ipt = list(position)
            # ipt.extend(list(goal))
            dist_y = position[0] - goal[0]
            dist_x = position[1] - goal[1]
            ipt = [dist_y, dist_x]
            # add on obstacle coordinates, if they're there.
            for obs in self.board.obstacles:
                i = list(obs.position())
                dist_y = position[0] - i[0]
                dist_x = position[1] - i[1]
                ipt.extend(i)
        return ipt, dist

    def get_distance(self, position, goal):
        #return np.abs(position - np.array(self.goal)).sum()
        return np.linalg.norm(np.array(position) - np.array(goal))

    def plan_movement(self, debug = False):
        # use the deterministic strategy
        ipt, dist = self.get_input()
        # dist_y = ipt[0] - ipt[2]
        # dist_x = ipt[1] - ipt[3]
        dist_y = ipt[0]
        dist_x = ipt[1]
        if debug == True: pdb.set_trace()
        if dist == 1:
            # chill
            choice = 4
        else:
            # do something
            self.at_goal = 0
            if abs(dist_y) < abs(dist_x):
                # x distance is greater
                if dist_x < 0:
                    # less than 0, so move right
                    choice = 0
                else:
                    choice = 1
            else:
                # y distance is greater or equal
                if dist_y < 0:
                    # less than 0, so move up
                    choice = 2
                else:
                    choice = 3
            d = np.random.random()
            # explore/exploit
            if d < self.epsilon:
                choice = randint(0, 4)
        return choice

    def step(self, choice = None):
        position = self.figure.position()
        goal = self.goal
        dist = self.get_distance(position, goal)
        if choice == None:
            choice = self.plan_movement()
        self.last_choice = choice
        if (dist == 1):# and (choice == 0):
            self.at_goal += 1
        else:
            self.at_goal = 0
        if choice != 4:
            action = self.actions[choice]
            # status = "Moving: " + str(action) + ", Choice: " + str(choice)
            # print(status)
            try:
                self.figure.move(y = action[0], x = action[1], relative = True)
            except:
                # print("Movement not allowed")
                choice = 4
                # self.step(choice = choice)
        return choice

if __name__=='__main__':
    test_game = NaviGame(moving_target = False)
    test_game.setup()
    make_gif(test_game, 15)
