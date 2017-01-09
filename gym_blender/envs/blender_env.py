import os, subprocess, time, signal
import gym
from gym import error, spaces
from gym import utils
from gym.utils import seeding
import numpy as np

try:
    import ble
except ImportError as e:
    raise error.DependencyNotInstalled("{}. (HINT: you can install ble dependencies with 'pip install gym[ble].)'".format(e))

    
import logging
logger = logging.getLogger(__name__)



class BleEnv(gym.Env, utils.EzPickle):
    metadata = {'render.modes': ['human']}

    def __init__(self, game_path='ridge_game.blend'):
        self.viewer = None
        self.server_process = None
        self.game_path = game_path
        self.env = ble.ble_environment(game_path)
        
        self.env.start_game()
        self.env.start_UDP()
        self.env.getMinimalActionSet()
        # initialize with random action
        action = self.env.legal_action_set[np.random.randint(len(self.env.legal_action_set))]
        self.env.act(action)
        self.env.iterate()
        self.observation_space = spaces.Box(low=-1, high=1,
                                            shape=(self.env.getScreenDims()))
        
        self.action_space = spaces.Tuple((spaces.Discrete(len(self.env.legal_action_set))))
        
    def __del__(self):
        self.env.test_send("off")
        self.env.iterate()
        self.env.iterate()
        del self.env
        if self.viewer is not None:
            os.kill(self.viewer.pid, signal.SIGKILL)

    def _step(self, action):
        for i in range(1):
            self.env.act(action)
            self.status = self.env.iterate()
        reward = self.env.get_reward()
        ob = self.env.getScreenGrayscale()
        episode_over = self.env.get_game_over()
        return ob, reward, episode_over, {}
    
    def _reset(self):
        self.env.reset_game()
        action = self.env.legal_action_set[np.random.randint(len(self.env.legal_action_set))]
        self.env.act(action)
        self.env.iterate()
        ob = self.env.getScreenGrayscale()
        return ob
    
    
    def _render(self, mode='human', close=False):
        """ ble environement can only run in human mode currently, and 
        game is rendered directly in blender (blender game engine cannot run in )"""
        pass
