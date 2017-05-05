# ReadBGE_UDPsocket sample Blender Script to read and act on data from UDP port
# Must get connection from Always sensor which feeds AND Controller
# and a connection from Property sensor
import math
import numpy
import pickle

import bge
import bgl
from bge import logic as GameLogic

scene = bge.logic.getCurrentScene()
contr = GameLogic.getCurrentController()
obj = contr.owner
near = contr.sensors["Near"]

legal_action_set = ["forward", "backward", "left", "right"]


class BlenderGameInteface(object):
    def __init__(self):

        self.checkpoints = [obj.name for obj in scene.objects if 'checkpoint' in obj.name]

    def send_data(self, Data):
        Data = pickle.dumps(Data, protocol=2)
        GameLogic.socketClient.sendto(Data, ("localhost", 10000))

    def send_string(self, Data):
        GameLogic.socketClient.sendto(Data, ("localhost", 10000))

    def get_screen_dims(self):
        b = bgl.Buffer(bgl.GL_INT, 4)
        bgl.glGetIntegerv(bgl.GL_VIEWPORT, b)
        bgl.glReadBuffer(bgl.GL_FRONT)
        pix = bgl.Buffer(bgl.GL_INT, b[2] * b[3])
        bgl.glReadPixels(b[0], b[1], b[2], b[3], bgl.GL_LUMINANCE, bgl.GL_INT, pix)
        x = b[2]
        y = b[3]
        self.send_data((x, y))

    def send_image(self):
        """
        sends serialized image, uint8 image

        """
        b = bgl.Buffer(bgl.GL_INT, 4)
        bgl.glGetIntegerv(bgl.GL_VIEWPORT, b)
        bgl.glReadBuffer(bgl.GL_FRONT)
        pix = bgl.Buffer(bgl.GL_INT, b[2] * b[3])
        bgl.glReadPixels(b[0], b[1], b[2], b[3], bgl.GL_LUMINANCE, bgl.GL_INT, pix)
        x = b[2]
        y = b[3]
        array = numpy.zeros((x * y), dtype=numpy.uint8)
        array[0:x * y] = pix
        self.send_data((x, y))
        for i in range(0, len(array), 400):
            self.send_data(array[i:i + 400])

    def get_reward(self):
        reward = 0

        hit_List = near.hitObjectList

        for checkpoint in self.checkpoints:
            checkpoint_num = int(checkpoint.split('_')[1])
            if checkpoint in hit_List and obj["check_point"] == checkpoint_num - 1:
                reward = 1
                obj["check_point"] += 1

        self.send_data(reward)

    def check_game_over(self):
        hit_List = near.hitObjectList

        if any(k in hit_List for k in ["Wall_1", "Wall_2", "Wall_3"]):
            scene.objects["Player"].localPosition = [-28.0, 0.0, 1.2]
            scene.objects["Player"].worldOrientation = [0.0, 0.0, -1.6]
            obj["episode_frame"] = 0
            obj["game_over"] = 1
            reward = -1

        self.send_data(obj["game_over"])

        if obj["game_over"] == 1:
            print("GAME OVER")

    @staticmethod
    def update_frame_number():
        obj["frame"] += 1
        obj["episode_frame"] += 1

    @staticmethod
    def get_frame_number():
        frame_number = math.floor(obj["frame"])
        episode_frame_number = obj["episode_frame"]
        return frame_number, episode_frame_number

    @staticmethod
    def reset_game():
        scene.objects["Player"].localPosition = [-28.0, 0.0, 1.2]
        scene.objects["Player"].worldOrientation = [0.0, 0.0, -1.6]
        obj["episode_frame"] = 0
        obj["game_over"] = 0
        obj["frame"] = 0
        obj["check_point"] = 0

    @staticmethod
    def move(dx):
        pos_x = scene.objects["Player"].localPosition[0]
        pos_y = scene.objects["Player"].localPosition[1]
        pos_z = scene.objects["Player"].localPosition[2]
        rot = scene.objects["Player"].worldOrientation.to_euler()
        rot_z = rot[2]
        pos_x += -dx * math.sin(rot_z)
        pos_y += dx * math.cos(rot_z)
        scene.objects["Player"].localPosition = [pos_x, pos_y, pos_z]

    @staticmethod
    def turn(dtheta):
        rot = scene.objects["Player"].worldOrientation.to_euler()
        rot_z = rot[2]
        rot_z -= dtheta
        scene.objects["Player"].worldOrientation = [0.0, 0.0, rot_z]


gi = BlenderGameInteface()

legal_action_set = [a.encode('ascii', 'ignore') for a in legal_action_set]

frame_number, episode_frame_number = gi.get_frame_number()

msg = ""
if obj['connected'] == 'c':

    while msg != "proceed":
        try:

            msg = GameLogic.socketClient.recvfrom(1024)
            print(msg[0])
            msg = pickle.loads(msg[0])
            print(msg[0])

            if msg == "frame":
                gi.send_data(frame_number)

            elif msg == "episode_frame":
                gi.send_data(episode_frame_number)

            elif msg == "image":
                gi.send_image()

            elif msg == "reset_game":
                gi.reset_game()

            elif msg == "game_over":
                gi.check_game_over()

            elif msg == "reward":
                gi.get_reward()

            elif msg == "screen_dims":
                gi.get_screen_dims()

            elif msg == "action_set":
                gi.send_data(legal_action_set)

            elif msg == "forward":
                gi.move(2)

            elif msg == "backward":
                gi.move(2)

            elif msg == "left":
                gi.turn(0.2)

            elif msg == "right":
                gi.turn(-0.2)

            elif msg == "off":
                GameLogic.endGame()

        except Exception as e:
            print(e)

gi.update_frame_number()
