import matplotlib as plt
import pylab as pl
import numpy as np
import imageio
# import os, sys
from os import listdir
from os.path import isfile, join
from IPython import display

def draw_game(game, mpl=True, save = False, filename = "game_image.png", show = True):
    s = np.array(game.board.cells)
    color = lambda i: 0 if i == None else i.color
    colormask = np.vectorize(color)
    s_colors = colormask(s)
    if mpl==True:
        pl.close('all')
        ax = pl.gca()
        ax.set_aspect('equal')
        pl.pcolor(s_colors)
        ax.tick_params(labelbottom='off', labelleft='off')
        # pl.colorbar()
        pl.title(game.display_str)
        if save == True: pl.savefig(filename)
        if show == True: pl.show();
    else:
        print(s_colors)

def step_game(game, n=1):
    for i in range(n):
        game.step()

def step_test(game, n=10):
    for i in range(n):
        s0 = np.array(game.board.cells)
        game.step()
        s1 = np.array(game.board.cells)
        if s0.all() == s1.all():
            pass
        else:
            draw_game(game)

def step_and_draw_game(game, mpl=True, save = False, filename = None, show = True):
    step_game(game)
    draw_game(game, mpl, save, filename, show)

def animate_game(game, n, mpl=True, save = False, show = True):
    if n > 1000:
        print("n too large")
        return
    for i in range(n):
        if (n >= 10) and (n < 100) and (i < 10):
            fn = "0" + str(i)
        elif (n >= 100) and (i < 10):
            fn = "00" + str(i)
        elif (n >= 100) and (i < 100):
            fn = "0" + str(i)
        else:
            fn = str(i)
        filename =  "anim/" + fn + ".png"
        if show == True:
            display.clear_output(wait=True)
            display.display(step_and_draw_game(game, mpl, save, filename));
        else:
            step_and_draw_game(game, mpl, save, filename, show)

def get_strategies(game):
    for figure in game.board.figures:
        print(figure.strategy.deltaY, figure.strategy.deltaX)

def make_gif(game, steps, filename = "compiled"):
    print("stepping game and saving images...")
    animate_game(game, steps, save = True, show = False)
    print("compiling gif")
    mypath = "anim/"

    filenames = [join(mypath, f) for f in listdir(mypath) if isfile(join(mypath, f))]
    filenames.sort()
    file_str = filename + '.gif'
    with imageio.get_writer(file_str, mode='I', duration=0.25) as writer:
        for imname in filenames:
            if (imname[0:6] != 'anim/.'):
                image = imageio.imread(imname)
                writer.append_data(image)
    print("gif made")
