import numpy as np
import os
import signal
import inspect

import gym
from gym import error, spaces
from gym import utils

try:
    from blender_interface import BlenderInterface
except ImportError as e:
    raise error.DependencyNotInstalled("{}. (HINT: you can install ble "
                                       "dependencies with 'pip install gym[ble].)'".format(e))


import logging
logger = logging.getLogger(__name__)


class BleEnv(gym.Env, utils.EzPickle):
    metadata = {'render.modes': ['human']}

    def __init__(self, game_path=''):
        super(BleEnv, self).__init__()
        self.viewer = None
        self.server_process = None
        self.game_path = game_path
        self.blender_interface = BlenderInterface(game_path)

        self.blender_interface.start_game()
        self.blender_interface.start_udp()
        self.blender_interface.get_minimal_action_set()
        # initialize with random action
        action = self.blender_interface.legal_action_set[np.random.randint(len(self.blender_interface.legal_action_set))]
        self.blender_interface.act(action)
        self.blender_interface.step()
        self.observation_space = spaces.Box(low=-1, high=1,
                                            shape=(self.blender_interface.get_screen_dims()))

        self.action_space = spaces.Discrete(len(self.blender_interface.legal_action_set))

    def __del__(self):
        del self.blender_interface
        if self.viewer is not None:
            os.kill(self.viewer.pid, signal.SIGKILL)

    def _step(self, action):
        for i in range(1):
            self.blender_interface.act(action)
            self.blender_interface.step()
        reward = self.blender_interface.get_reward()
        ob = self.blender_interface.get_screen_grayscale()
        episode_over = self.blender_interface.get_game_over()
        return ob, reward, episode_over, {}

    def _reset(self):
        self.blender_interface.reset_game()
        rand_action = np.random.choice(self.blender_interface.legal_action_set)
        self.blender_interface.act(rand_action)
        self.blender_interface.step()
        ob = self.blender_interface.get_screen_grayscale()
        return ob

    def _render(self, mode='human', close=False):
        """ ble environement can only run in human mode currently, and 
        game is rendered directly in blender (blender game engine cannot run in )"""
        pass


class RidgeEnv(BleEnv):

    def __init__(self, game_path=None):
        if game_path is None:
            # find absolute path to the blenderInterface directories
            game_path = os.path.dirname(inspect.getabsfile(BlenderInterface))
            # now get game path:
            game_path = os.path.dirname(os.path.dirname(game_path))
            game_path = os.path.join(game_path, 'games/ridge/ridge.blend')

        super(RidgeEnv, self).__init__(game_path=game_path)
