import socket
import struct
import math 
import sys, time
import pickle
import numpy as np
import sys
import subprocess
import time, signal, os

class ble_environment:
    
    def __init__(self,blender_filename):
        self.game_name = blender_filename
        self.game_over = 0
        
    def __del__(self):
        print("stopping")
        os.kill(self.server_process.pid, signal.SIGINT)

    
    def start_game(self):
        print "starting"
        args = ['blender',self.game_name,'-P','start_engine.py']
        self.server_process = subprocess.Popen(args, shell=False)
        time.sleep(3.0)

    def start_UDP(self):
        #Connect through socket to the blender game engine (UDP):
        # replace localhost with network name of game machine defined in game blend
        self.HOST, self.PORT_SND, self.PORT_RCV = "localhost", 9999, 10000

        # SOCK_DGRAM is the socket type to use for UDP sockets
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.HOST, self.PORT_RCV))
        print "UDP started"
        return self.sock

    def test_send(self,data):
        data = pickle.dumps((data))
        self.sock.sendto(data, (self.HOST, self.PORT_SND))
        
    def test_send_no_pickle(self,data):
        self.sock.sendto(data, (self.HOST, self.PORT_SND))

    def test_receive(self):
        test_input = self.sock.recvfrom(1024)
        test_input = pickle.loads(test_input[0])
        print "test input is ", test_input

    def get_frame_number(self):
        data = pickle.dumps(("frame"))
        self.sock.sendto(data, (self.HOST, self.PORT_SND))
        frame = self.sock.recvfrom(1024)
        self.frame = pickle.loads(frame[0])
        #print "frame # is ", frame

    def get_episode_frame_number(self):
        data = pickle.dumps(("episode_frame"))
        self.sock.sendto(data, (self.HOST, self.PORT_SND))
        episode_frame = self.sock.recvfrom(1024)
        self.episode_frame = pickle.loads(episode_frame[0])
        #print "frame # is ", frame
        
    def getMinimalActionSet(self):
        data = pickle.dumps(("action_set"))
        self.sock.sendto(data, (self.HOST, self.PORT_SND))
        legal_action_set = self.sock.recvfrom(1024)
        self.legal_action_set = pickle.loads(legal_action_set[0])
                    
    def iterate(self):
        data = pickle.dumps(("proceed"))
        self.sock.sendto(data, (self.HOST, self.PORT_SND))

    def act(self,action):
        data = pickle.dumps((action))
        self.sock.sendto(data, (self.HOST, self.PORT_SND))

    def get_game_over(self):
        data = pickle.dumps(("game_over"))
        self.sock.sendto(data, (self.HOST, self.PORT_SND))
        go = self.sock.recvfrom(1024)
        go = pickle.loads(go[0])
        return go
    
    def reset_game(self):
        data = pickle.dumps(("reset_game"))
        self.sock.sendto(data, (self.HOST, self.PORT_SND))

    def getScreenDims(self):
        data = pickle.dumps(("screen_dims"))
        self.sock.sendto(data, (self.HOST, self.PORT_SND))
        img_size = self.sock.recvfrom(1024)
        img_size = pickle.loads(img_size[0])
        return img_size[0], img_size[1]

    def getScreenGrayscale(self):
        data = pickle.dumps(("image"))
        self.sock.sendto(data, (self.HOST, self.PORT_SND))
        img_size = self.sock.recvfrom(1024)
        self.img_size = pickle.loads(img_size[0])
        self.image = np.zeros((self.img_size[0]*self.img_size[1]),dtype=np.uint8)
        for i in range(0, self.img_size[0]*self.img_size[1], 400):
            image = self.sock.recvfrom(1024)
            image = pickle.loads(image[0])
            self.image[i:i+400] = image
        
        buffer = self.image.reshape(-1,self.img_size[0])
        return buffer

    def get_reward(self):
        data = pickle.dumps(("reward"))
        self.sock.sendto(data, (self.HOST, self.PORT_SND))
        reward = self.sock.recvfrom(1024)
        self.reward = pickle.loads(reward[0])
        return self.reward
    
