# Blender python script to open UDP port for listening

# must get connections from Always sensor with pulse mode deactivated (runs only at startup)

import socket
from bge import logic as GameLogic

# reference to main object
contr = GameLogic.getCurrentController()
game_state = contr.owner


def main():
    game_state["game_over"] = 0
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
    game_state['connected'] = 'c'
    print(host)
    print(port)

if __name__ == '__main__':
    main()
