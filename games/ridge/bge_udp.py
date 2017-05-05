# Blender python script to open UDP port for listening

# must get connections from Always sensor which feeds AND controller

import socket
from bge import logic as GameLogic

# reference to main object
contr = GameLogic.getCurrentController()
obj = contr.owner

# If not socket not opn, open it, else do nothing
if obj['connected'] == '':
    # obj["frame"] = 0
    # obj["episode_frame"] = 0
    # obj["game_over"] = 0
    # obj["check_point"] = 0
    # computer name and port number
    host = "localhost"  # replace with net name or IP address of game machine
    # host = "192.168.1.100"  # a static IP you might assign on a cable/dsl modem router box
    port = 9999  # socket for UDP
    GameLogic.socketClient = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # accept messages from client to this host and port
    GameLogic.socketClient.bind((host, port))
    # nonblocking mode
    GameLogic.socketClient.setblocking(0)
    # Set object property ftp enable action script
    obj['connected'] = 'c'
    print(host)
    print(port)
