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


# class BlenderGameInteface(object):
#
#     def __init__(self, scene, contr):
#         self.game_state = contr.owner
#         self.scene = scene
#         self.contr = contr
#         self.legal_action_set = []
#
#     def act(self, action):
#         pass
#
#     def get_reward(self):
#         pass
#
#     def check_game_over(self):
#         pass
#
#     def get_screen_dims(self):
#         self.get_data((SCREEN_W, SCREEN_H))
#
#     def get_image(self):
#         """
#         sends serialized image, uint8 image
#
#         """
#         _buffer = bgl.Buffer(bgl.GL_INT, 4)
#         bgl.glGetIntegerv(bgl.GL_VIEWPORT, _buffer)
#         bgl.glReadBuffer(bgl.GL_FRONT)
#         pix = bgl.Buffer(bgl.GL_INT, _buffer[2] * _buffer[3])
#         bgl.glReadPixels(_buffer[0], _buffer[1], _buffer[2], _buffer[3], bgl.GL_LUMINANCE, bgl.GL_INT, pix)
#         array = numpy.zeros((SCREEN_W * SCREEN_H), dtype=numpy.uint8)
#         array[0:SCREEN_W * SCREEN_H] = pix
#         self.get_data((SCREEN_W, SCREEN_H))
#         for i in range(0, len(array), 400):
#             self.get_data(array[i:i + 400])
#
#     def reset_game(self):
#         self.game_state["game_over"] = 0
#
#     def get_legal_action_set(self):
#         self.get_data(self.legal_action_set)
#
#     @staticmethod
#     def terminate():
#         game_logic.endGame()
#
#     @staticmethod
#     def get_data(data):
#         data = pickle.dumps(data, protocol=2)
#         game_logic.socketClient.sendto(data, ("localhost", 10000))
#
#
# class RidgeGameInterface(BlenderGameInteface):
#
#     def __init__(self, scene, contr):
#         """
#         Interface for the game Ridge, inherits from the BlenderGameInterface.
#         In Ridge, the player goal is to walk the furthest on a plank without
#         falling.
#
#         This class implements the act, reward, game over, reset functions specific
#         to this game.
#
#         :param scene: blender game engine scene object
#         :param contr: blender game engine controller object
#         """
#         super(RidgeGameInterface, self).__init__(scene, contr)
#         self.checkpoints = [obj.name for obj in self.scene.objects if 'checkpoint' in obj.name]
#         self.new_sensor = contr.sensors["Near"]
#         self.legal_action_set = ["forward", "backward", "left", "right"]
#
#     def act(self, action):
#         assert (action in self.legal_action_set)
#         if action == 'forward':
#             self._move(dx=0.2)
#         elif action == 'backward':
#             self._move(dx=0.2)
#         elif action == 'left':
#             self._turn(dtheta=-0.2)
#         elif action == 'right':
#             self._turn(dtheta=0.2)
#
#     def get_reward(self):
#         reward = 0
#
#         hit_List = self.new_sensor.hitObjectList
#         for checkpoint in self.checkpoints:
#             checkpoint_num = int(checkpoint.split('_')[1])
#             if checkpoint in hit_List and self.game_state["check_point"] == checkpoint_num - 1:
#                 print(checkpoint, self.game_state["check_point"])
#                 reward = 1
#                 self.game_state["check_point"] += 1
#
#         self.get_data(reward)
#
#     def check_game_over(self):
#         hit_List = self.new_sensor.hitObjectList
#
#         if any(k in hit_List for k in ["Wall_1", "Wall_2", "Wall_3"]):
#             self.scene.objects["Player"].localPosition = [-28.0, 0.0, 1.2]
#             self.scene.objects["Player"].worldOrientation = [0.0, 0.0, -1.6]
#             self.game_state["game_over"] = 1
#
#         self.get_data(self.game_state["game_over"])
#
#         if self.game_state["game_over"] == 1:
#             print("GAME OVER")
#
#     def reset_game(self):
#         super(RidgeGameInterface, self).reset_game()
#         self.scene.objects["Player"].localPosition = [-28.0, 0.0, 1.2]
#         self.scene.objects["Player"].worldOrientation = [0.0, 0.0, -1.6]
#         self.game_state["check_point"] = 0
#
#     def _move(self, dx):
#         pos_x = self.scene.objects["Player"].localPosition[0]
#         pos_y = self.scene.objects["Player"].localPosition[1]
#         pos_z = self.scene.objects["Player"].localPosition[2]
#         rot = self.scene.objects["Player"].worldOrientation.to_euler()
#         rot_z = rot[2]
#         pos_x += -dx * math.sin(rot_z)
#         pos_y += dx * math.cos(rot_z)
#         self.scene.objects["Player"].localPosition = [pos_x, pos_y, pos_z]
#
#     def _turn(self, dtheta):
#         rot = self.scene.objects["Player"].worldOrientation.to_euler()
#         rot_z = rot[2]
#         rot_z -= dtheta
#         self.scene.objects["Player"].worldOrientation = [0.0, 0.0, rot_z]


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

if __name__ == "__main__":
    main()
