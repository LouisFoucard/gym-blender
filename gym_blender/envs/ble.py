import numpy as np
import os
import pickle
import signal
import socket
import subprocess
import time


class BlenderInterface:
    
    def __init__(self, blender_filename):
        self.game_name = blender_filename
        self.game_over = 0
        self.server_process = None
        self.HOST = "localhost"
        self.PORT_SND = 9999
        self.PORT_RCV = 10000
        self.sock = None
        self.frame = None
        self.episode_frame = None
        self.legal_action_set = []
        self.img_size = None
        self.image = np.empty(0)
        self.reward = 0
        
    def __del__(self):
        print("stopping")
        data = pickle.dumps("terminate")
        self.sock.sendto(data, (self.HOST, self.PORT_SND))
        time.sleep(0.1)
        os.kill(self.server_process.pid, signal.SIGKILL)
    
    def start_game(self):
        print("starting")
        args = ['blender', self.game_name, '-P', 'games/start_engine.py']
        self.server_process = subprocess.Popen(args, shell=False)
        time.sleep(3.0)

    def start_udp(self):
        # Connect through socket to the blender game engine (UDP):
        # SOCK_DGRAM is the socket type to use for UDP sockets
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.HOST, self.PORT_RCV))
        print "UDP started"
        return self.sock

    def get_frame_number(self):
        data = pickle.dumps("get_data-frame_number")
        self.sock.sendto(data, (self.HOST, self.PORT_SND))
        frame = self.sock.recvfrom(1024)
        self.frame = pickle.loads(frame[0])

    def get_episode_frame_number(self):
        data = pickle.dumps("get_data-episode_frame")
        self.sock.sendto(data, (self.HOST, self.PORT_SND))
        episode_frame = self.sock.recvfrom(1024)
        self.episode_frame = pickle.loads(episode_frame[0])
        
    def get_minimal_action_set(self):
        data = pickle.dumps("get_data-legal_action_set")
        self.sock.sendto(data, (self.HOST, self.PORT_SND))
        legal_action_set = self.sock.recvfrom(1024)
        self.legal_action_set = pickle.loads(legal_action_set[0])
                    
    def iterate(self):
        data = pickle.dumps("proceed")
        self.sock.sendto(data, (self.HOST, self.PORT_SND))

    def act(self, action):
        data = pickle.dumps('act-'+action)
        self.sock.sendto(data, (self.HOST, self.PORT_SND))

    def get_game_over(self):
        data = pickle.dumps("check_game_over")
        self.sock.sendto(data, (self.HOST, self.PORT_SND))
        go = self.sock.recvfrom(1024)
        go = pickle.loads(go[0])
        return go
    
    def reset_game(self):
        data = pickle.dumps("reset_game")
        self.sock.sendto(data, (self.HOST, self.PORT_SND))

    def get_screen_dims(self):
        data = pickle.dumps("get_screen_dims")
        self.sock.sendto(data, (self.HOST, self.PORT_SND))
        img_size = self.sock.recvfrom(1024)
        img_size = pickle.loads(img_size[0])
        return img_size[0], img_size[1]

    def get_screen_grayscale(self):
        data = pickle.dumps("get_image")
        self.sock.sendto(data, (self.HOST, self.PORT_SND))
        img_size = self.sock.recvfrom(1024)
        self.img_size = pickle.loads(img_size[0])
        self.image = np.zeros((self.img_size[0]*self.img_size[1]), dtype=np.uint8)
        for i in range(0, self.img_size[0]*self.img_size[1], 400):
            image = self.sock.recvfrom(1024)
            image = pickle.loads(image[0])
            self.image[i:i+400] = image
        
        _buffer = self.image.reshape(-1, self.img_size[0])
        return _buffer

    def get_reward(self):
        data = pickle.dumps("get_reward")
        self.sock.sendto(data, (self.HOST, self.PORT_SND))
        reward = self.sock.recvfrom(1024)
        self.reward = pickle.loads(reward[0])
        return self.reward
