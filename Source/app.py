#! /usr/bin/env python

import curses
import logger
from logger import log
from time import sleep

game = "BirdGame"
speed = 10
amountOfFigures = 20
amountOfNeighbours = 1

class Application:
    def __init__(self, screen, logger):
        self.screen = screen
        self.logger = logger
        self.main()

    def main(self):
        self.view = View(self)
        self.model = Model(self)
        self.controller = Controller(self)
        self.wireUp()
        self.controller.loop()

    def wireUp(self):
        self.view.logger = self.logger
        self.view.game = self.model.game

class Controller:
    def __init__(self, app):
        self.app = app

    def loop(self):
        self.app.screen.nodelay(1)
        while True:
            if self.app.screen.getch() == ord('q'): break
            self.app.model.step()
            self.app.view.draw()
            sleep(1.0/speed)

class Model:
    def __init__(self, app):
        self.app = app
        height, width = self.app.view.canvas.getmaxyx()
        if game == "MoskitoGame":
            from moskito_game import MoskitoGame
            self.game = MoskitoGame(height - 2, width - 2, amountOfFigures)
        elif game == "BirdGame":
            from bird_game import BirdGame
            self.game = BirdGame(height - 2, width - 2, amountOfFigures)
            self.game.amountOfNeighbours = amountOfNeighbours
        self.game.setup()

    def step(self):
        self.game.step()

class View:
    def __init__(self, app):
        logger.log("Hit q to quit")
        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
        try: curses.curs_set(0)
        except: pass
        self.setupRoot(app.screen)
        self.setupCanvas()
        self.setupLog()

    def child(self, parent, position):
        return curses.newwin(*self.layout(parent, position))

    def draw(self):
        self.drawLog()
        self.drawGame()

    def drawGame(self):
        board = self.game.board
        for y in range(board.height):
            for x in range(board.width):
                self.canvas.addstr(y + 1, x + 1, board.symbol(y,x),
                        curses.color_pair(board.color(y,x)))
        self.canvas.refresh()

    def drawLog(self):
        msgs = self.logger.msgs
        self.log.erase()
        self.log.box()
        lines = msgs[-self.heightOf(self.log):]
        for n in range(len(lines)):
            self.log.addstr(n + 1, 2, lines[n])
        self.log.refresh()

    def layout(self, parent, position):
        y, x = parent.getbegyx()
        height, width = parent.getmaxyx()
        halfHeight = height / 2
        halfWidth = width / 2
        if position == "left":
            return height, halfWidth, y, x
        if position == "right":
            return height, halfWidth, y, x + halfWidth
        if position == "top":
            return halfHeight, width, y, x
        if position == "bottom":
            return halfHeight, width, y + halfHeight , x

    def setupRoot(self, screen):
        self.root = screen
        self.root.box()
        self.root.refresh()

    def setupCanvas(self):
        self.canvas = self.child(self.root, 'left')
        self.canvas.box()
        self.canvas.refresh()

    def setupLog(self):
        self.log = self.child(self.root, 'right')
        self.log.box()
        self.log.refresh()

    def heightOf(self, window):
        return window.getmaxyx()[0] - 2

if __name__ == '__main__':
    curses.wrapper(Application, logger)

