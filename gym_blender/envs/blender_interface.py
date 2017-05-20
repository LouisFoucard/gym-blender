import numpy as np
import os
import pickle
import signal
import socket
import subprocess
import time


class BlenderInterface:
    
    def __init__(self, blender_filename, host='localhost', port_send=9999, port_rcv=10000):
        self.game_name = blender_filename
        self.game_over = 0
        self.server_process = None
        self.HOST = host
        self.PORT_SND = port_send
        self.PORT_RCV = port_rcv
        self.sock = None
        self.frame = None
        self.episode_frame = None
        self.legal_action_set = []
        self.img_size = None
        self.image = np.empty(0)
        self.reward = 0
        self.buflen = 1024
        
    def __del__(self):
        """exit gracefully"""
        print("stopping")
        cmd = pickle.dumps("terminate")
        self.sock.sendto(cmd, (self.HOST, self.PORT_SND))
        time.sleep(0.1)
        self.sock.close()
        os.kill(self.server_process.pid, signal.SIGKILL)
    
    def start_game(self):
        print("starting")
        start_script_path = os.path.join(os.path.dirname(self.game_name), 'start_engine.py')
        args = ['blender', self.game_name, '-P', start_script_path]
        self.server_process = subprocess.Popen(args, shell=False)
        time.sleep(3.0)

    def start_udp(self):
        # Connect through socket (UDP) to the blender game engine:
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.HOST, self.PORT_RCV))
        print "UDP started"
        return self.sock

    def get_minimal_action_set(self):
        cmd = pickle.dumps("get_legal_action_set")
        self.sock.sendto(cmd, (self.HOST, self.PORT_SND))
        legal_action_set = self.sock.recvfrom(self.buflen)
        self.legal_action_set = pickle.loads(legal_action_set[0])
                    
    def step(self):
        cmd = pickle.dumps("step")
        self.sock.sendto(cmd, (self.HOST, self.PORT_SND))

    def act(self, action):
        cmd = pickle.dumps('act-'+action)
        self.sock.sendto(cmd, (self.HOST, self.PORT_SND))

    def get_game_over(self):
        cmd = pickle.dumps("check_game_over")
        self.sock.sendto(cmd, (self.HOST, self.PORT_SND))
        go = self.sock.recvfrom(self.buflen)
        go = pickle.loads(go[0])
        return go
    
    def reset_game(self):
        cmd = pickle.dumps("reset_game")
        self.sock.sendto(cmd, (self.HOST, self.PORT_SND))

    def get_screen_dims(self):
        cmd = pickle.dumps("get_screen_dims")
        self.sock.sendto(cmd, (self.HOST, self.PORT_SND))
        img_size = self.sock.recvfrom(self.buflen)
        img_size = pickle.loads(img_size[0])
        return img_size[0], img_size[1]

    def get_screen_grayscale(self):
        cmd = pickle.dumps("get_image")
        self.sock.sendto(cmd, (self.HOST, self.PORT_SND))
        img_size = self.sock.recvfrom(self.buflen)
        self.img_size = pickle.loads(img_size[0])
        self.image = np.zeros((self.img_size[0]*self.img_size[1]), dtype=np.uint8)
        for i in range(0, self.img_size[0]*self.img_size[1], 400):
            image = self.sock.recvfrom(self.buflen)
            image = pickle.loads(image[0])
            self.image[i:i+400] = image
        
        _buffer = self.image.reshape(-1, self.img_size[0])
        return _buffer

    def get_reward(self):
        cmd = pickle.dumps("get_reward")
        self.sock.sendto(cmd, (self.HOST, self.PORT_SND))
        reward = self.sock.recvfrom(self.buflen)
        self.reward = pickle.loads(reward[0])
        return self.reward
