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

    def __init__(self, scene, contr, near_sensor, legal_action_set, game_state):
        self.game_state = game_state
        self.scene = scene
        self.contr = contr
        self.near_sensor = near_sensor
        self.legal_action_set = legal_action_set
        self.checkpoints = [obj.name for obj in self.scene.objects if 'checkpoint' in obj.name]

        _buffer = bgl.Buffer(bgl.GL_INT, 4)
        bgl.glGetIntegerv(bgl.GL_VIEWPORT, _buffer)
        bgl.glReadBuffer(bgl.GL_FRONT)
        pix = bgl.Buffer(bgl.GL_INT, _buffer[2] * _buffer[3])
        bgl.glReadPixels(_buffer[0], _buffer[1], _buffer[2], _buffer[3], bgl.GL_LUMINANCE, bgl.GL_INT, pix)
        self.x = _buffer[2]
        self.y = _buffer[3]

    def act(self, action):
        pass

    def get_reward(self):
        pass

    def check_game_over(self):
        pass

    def get_screen_dims(self):
        self.get_data((self.x, self.y))

    def get_image(self):
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
        self.get_data((x, y))
        for i in range(0, len(array), 400):
            self.get_data(array[i:i + 400])

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
    def terminate():
        game_logic.endGame()

    @staticmethod
    def get_data(data):
        data = pickle.dumps(data, protocol=2)
        game_logic.socketClient.sendto(data, ("localhost", 10000))


legal_action_set = ["forward", "backward", "left", "right"]


class RidgeGameInterface(BlenderGameInteface):

    def __init__(self, scene, contr, near_sensor, legal_action_set, game_state):
        super(RidgeGameInterface, self).__init__(scene, contr, near_sensor, legal_action_set, game_state)

    def act(self, action):
        assert (action in self.legal_action_set)
        if action == 'forward':
            self._move(dx=0.2)
        elif action == 'backward':
            self._move(dx=0.2)
        elif action == 'left':
            self._turn(dtheta=-0.2)
        elif action == 'right':
            self._turn(dtheta=0.2)

    def get_reward(self):
        reward = 0

        hit_List = self.near_sensor.hitObjectList
        for checkpoint in self.checkpoints:
            checkpoint_num = int(checkpoint.split('_')[1])
            if checkpoint in hit_List and self.game_state["check_point"] == checkpoint_num - 1:
                print(checkpoint, self.game_state["check_point"])
                reward = 1
                self.game_state["check_point"] += 1

        self.get_data(reward)

    def check_game_over(self):
        hit_List = self.near_sensor.hitObjectList

        if any(k in hit_List for k in ["Wall_1", "Wall_2", "Wall_3"]):
            self.scene.objects["Player"].localPosition = [-28.0, 0.0, 1.2]
            self.scene.objects["Player"].worldOrientation = [0.0, 0.0, -1.6]
            self.game_state["episode_frame"] = 0
            self.game_state["game_over"] = 1

        self.get_data(self.game_state["game_over"])

        if self.game_state["game_over"] == 1:
            print("GAME OVER")

    def _move(self, dx):
        pos_x = self.scene.objects["Player"].localPosition[0]
        pos_y = self.scene.objects["Player"].localPosition[1]
        pos_z = self.scene.objects["Player"].localPosition[2]
        rot = self.scene.objects["Player"].worldOrientation.to_euler()
        rot_z = rot[2]
        pos_x += -dx * math.sin(rot_z)
        pos_y += dx * math.cos(rot_z)
        self.scene.objects["Player"].localPosition = [pos_x, pos_y, pos_z]

    def _turn(self, dtheta):
        rot = self.scene.objects["Player"].worldOrientation.to_euler()
        rot_z = rot[2]
        rot_z -= dtheta
        self.scene.objects["Player"].worldOrientation = [0.0, 0.0, rot_z]


def main():
    global legal_action_set

    scene = bge.logic.getCurrentScene()
    contr = game_logic.getCurrentController()
    game_state = contr.owner
    near_sensor = contr.sensors["Near"]

    forward, backward, left, right = legal_action_set

    bgi = RidgeGameInterface(scene, contr, near_sensor, legal_action_set, game_state)
    frame_number, episode_frame_number = bgi.get_frame_number()

    msg = ""
    if game_state['connected'] == 'c':

        while msg != "proceed":
            try:

                msg = game_logic.socketClient.recvfrom(1024)
                msg = pickle.loads(msg[0])
                if msg == 'proceed':
                    continue

                if len(msg.split('-')) > 1:
                    f_name, arg = msg.split('-')
                    func = bgi.__getattribute__(f_name)
                    func(eval(arg))
                else:
                    f_name = msg
                    func = bgi.__getattribute__(f_name)
                    func()

            except Exception as e:
                print(e)

    bgi.update_frame_number()

if __name__ == "__main__":
    main()
