# Templated Blender Game Interface to read and act on data from UDP port

import pickle
from io import BlockingIOError

import bgl
from bge import logic as game_logic


def get_image_dims():
    # get image dimensions
    _buffer = bgl.Buffer(bgl.GL_INT, 4)  # image buffer
    bgl.glGetIntegerv(bgl.GL_VIEWPORT, _buffer)  # get image size
    return _buffer[2], _buffer[3]


def main():

    contr = game_logic.getCurrentController()

    bgi = contr.owner['bgi']
    bgi.screen_w, bgi.screen_h = get_image_dims()

    msg = ''
    while msg != 'step':
        try:
            # TODO get buflen from ble interface
            msg = game_logic.socketClient.recvfrom(1024)
            msg = pickle.loads(msg[0])
            if msg == 'step':
                continue

            if len(msg.split('-')) > 1:
                #  function call with argument
                f_name, arg = msg.split('-')
                func = bgi.__getattribute__(f_name)
                try:
                    func(eval(arg))
                except NameError:
                    func(arg)
            else:
                # function call without argument
                f_name = msg
                func = bgi.__getattribute__(f_name)
                func()

        except BlockingIOError:
            pass

if __name__ == '__main__':
    main()
