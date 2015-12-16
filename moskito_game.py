#! /usr/bin/env python

from random import random, sample, randint
from game import BoardGame
from board import Board
from figure import Figure

class MoskitoGame(BoardGame):
    def __init__(self, height, width, amount):
        self.board = Board(height, width)
        self.amount = amount

    def setup(self):
        for n in range(self.amount):
            figure = Figure(self.board)
            figure.strategy = MoskitoFigure(figure)
        self.board.figures()[0].color = 1

class MoskitoFigure:
    def __init__(self, figure):
        self.figure = figure
        self.board = figure.board
        self.placeIt()

    def modify(self):
        self.deltaX = randint(-2, 2)
        self.deltaY = randint(-2, 2)

    def step(self):
        if random() < 0.01: self.modify()
        try:
            self.figure.move(self.deltaY, self.deltaX, relative = True)
        except self.board.AboveWidthException:
            self.deltaX = -1
        except self.board.AboveHeightException:
            self.deltaY = -1
        except self.board.BelowWidthException:
            self.deltaX = 1
        except self.board.BelowHeightException:
            self.deltaY = 1
        except self.board.TakenException:
            self.deltaX = -self.deltaX
            self.deltaY = -self.deltaY

    def placeIt(self):
        x = sample(range(0, self.figure.board.width), 1)[0]
        y = sample(range(0, self.figure.board.height), 1)[0]
        self.modify()
        try:
            self.figure.add(y, x)
        except:
            self.placeIt()
