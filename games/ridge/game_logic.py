# ReadBGE_UDPsocket sample Blender Script to read and act on data from UDP port
# Must get connection from Always sensor which feeds AND Controller
# and a connection from Property sensor
import math
import numpy
import pickle

import bge
import bgl
from bge import logic as game_logic


class BlenderGameInteface(object):

    def __init__(self, scene, contr, near_sensor, game_state):
        self.game_state = game_state
        self.scene = scene
        self.contr = contr
        self.near_sensor = near_sensor
        self.checkpoints = [obj.name for obj in self.scene.objects if 'checkpoint' in obj.name]

    def get_screen_dims(self):
        _buffer = bgl.Buffer(bgl.GL_INT, 4)
        bgl.glGetIntegerv(bgl.GL_VIEWPORT, _buffer)
        bgl.glReadBuffer(bgl.GL_FRONT)
        pix = bgl.Buffer(bgl.GL_INT, _buffer[2] * _buffer[3])
        bgl.glReadPixels(_buffer[0], _buffer[1], _buffer[2], _buffer[3], bgl.GL_LUMINANCE, bgl.GL_INT, pix)
        x = _buffer[2]
        y = _buffer[3]
        self.send_data((x, y))

    def send_image(self):
        """
        sends serialized image, uint8 image

        """
        _buffer = bgl.Buffer(bgl.GL_INT, 4)
        bgl.glGetIntegerv(bgl.GL_VIEWPORT, _buffer)
        bgl.glReadBuffer(bgl.GL_FRONT)
        pix = bgl.Buffer(bgl.GL_INT, _buffer[2] * _buffer[3])
        bgl.glReadPixels(_buffer[0], _buffer[1], _buffer[2], _buffer[3], bgl.GL_LUMINANCE, bgl.GL_INT, pix)
        x = _buffer[2]
        y = _buffer[3]
        array = numpy.zeros((x * y), dtype=numpy.uint8)
        array[0:x * y] = pix
        self.send_data((x, y))
        for i in range(0, len(array), 400):
            self.send_data(array[i:i + 400])

    def get_reward(self):
        reward = 0

        hit_List = self.near_sensor.hitObjectList
        for checkpoint in self.checkpoints:
            checkpoint_num = int(checkpoint.split('_')[1])
            if checkpoint in hit_List and self.game_state["check_point"] == checkpoint_num - 1:
                print(checkpoint, self.game_state["check_point"])
                reward = 1
                self.game_state["check_point"] += 1

        self.send_data(reward)

    def check_game_over(self):
        hit_List = self.near_sensor.hitObjectList

        if any(k in hit_List for k in ["Wall_1", "Wall_2", "Wall_3"]):
            self.scene.objects["Player"].localPosition = [-28.0, 0.0, 1.2]
            self.scene.objects["Player"].worldOrientation = [0.0, 0.0, -1.6]
            self.game_state["episode_frame"] = 0
            self.game_state["game_over"] = 1

        self.send_data(self.game_state["game_over"])

        if self.game_state["game_over"] == 1:
            print("GAME OVER")

    def update_frame_number(self):
        self.game_state["frame"] += 1
        self.game_state["episode_frame"] += 1

    def get_frame_number(self):
        _frame_number = math.floor(self.game_state["frame"])
        _episode_frame_number = self.game_state["episode_frame"]
        return _frame_number, _episode_frame_number

    def reset_game(self):
        self.scene.objects["Player"].localPosition = [-28.0, 0.0, 1.2]
        self.scene.objects["Player"].worldOrientation = [0.0, 0.0, -1.6]
        self.game_state["episode_frame"] = 0
        self.game_state["game_over"] = 0
        self.game_state["frame"] = 0
        self.game_state["check_point"] = 0

    @staticmethod
    def send_data(data):
        data = pickle.dumps(data, protocol=2)
        game_logic.socketClient.sendto(data, ("localhost", 10000))

    @staticmethod
    def send_string(data):
        game_logic.socketClient.sendto(data, ("localhost", 10000))

    def move(self, dx):
        pos_x = self.scene.objects["Player"].localPosition[0]
        pos_y = self.scene.objects["Player"].localPosition[1]
        pos_z = self.scene.objects["Player"].localPosition[2]
        rot = self.scene.objects["Player"].worldOrientation.to_euler()
        rot_z = rot[2]
        pos_x += -dx * math.sin(rot_z)
        pos_y += dx * math.cos(rot_z)
        self.scene.objects["Player"].localPosition = [pos_x, pos_y, pos_z]

    def turn(self, dtheta):
        rot = self.scene.objects["Player"].worldOrientation.to_euler()
        rot_z = rot[2]
        rot_z -= dtheta
        self.scene.objects["Player"].worldOrientation = [0.0, 0.0, rot_z]


def main():
    scene = bge.logic.getCurrentScene()
    contr = game_logic.getCurrentController()
    game_state = contr.owner
    near_sensor = contr.sensors["Near"]
    legal_action_set = ["forward", "backward", "left", "right"]

    gi = BlenderGameInteface(scene, contr, near_sensor, game_state)

    legal_action_set = [a.encode('ascii', 'ignore') for a in legal_action_set]

    frame_number, episode_frame_number = gi.get_frame_number()

    msg = ""
    if game_state['connected'] == 'c':

        while msg != "proceed":
            try:

                msg = game_logic.socketClient.recvfrom(1024)
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
                    gi.move(0.2)

                elif msg == "backward":
                    gi.move(0.2)

                elif msg == "left":
                    gi.turn(0.2)

                elif msg == "right":
                    gi.turn(-0.2)

                elif msg == "off":
                    game_logic.endGame()

            except Exception as e:
                print(e)

    gi.update_frame_number()

if __name__ == "__main__":
    main()
