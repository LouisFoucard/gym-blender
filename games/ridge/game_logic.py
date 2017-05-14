# Templated Blender Game Interface to read and act on data from UDP port

import math
import numpy
import pickle
from io import BlockingIOError

import bge
import bgl
from bge import logic as game_logic

# get image dimensions
buffer = bgl.Buffer(bgl.GL_INT, 4)  # image buffer
bgl.glGetIntegerv(bgl.GL_VIEWPORT, buffer)  # get image size
SCREEN_W = buffer[2]
SCREEN_H = buffer[3]


def main():
    global SCREEN_W, SCREEN_H

    # scene = bge.logic.getCurrentScene()
    contr = game_logic.getCurrentController()

    # bgi = RidgeGameInterface(scene, contr)
    bgi = contr.owner["bgi"]
    bgi.screen_w = SCREEN_W
    bgi.screen_h = SCREEN_H

    msg = ""
    while msg != "step":
        try:

            msg = game_logic.socketClient.recvfrom(1024)
            msg = pickle.loads(msg[0])
            if msg == 'step':
                continue

            if len(msg.split('-')) > 1:
                f_name, arg = msg.split('-')
                func = bgi.__getattribute__(f_name)
                try:
                    func(eval(arg))
                except NameError:
                    func(arg)
            else:
                f_name = msg
                func = bgi.__getattribute__(f_name)
                func()

        except BlockingIOError:
            pass

    print('STEP')
    contr.owner['connected2'] = True

if __name__ == "__main__":
    main()
