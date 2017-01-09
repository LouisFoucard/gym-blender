# BLE_python_interface
Blender Learning Environment: BLE is a python interface for the blender game engine, to be added as an additional environment for Gym (https://github.com/openai/gym). Blender is a free 3D modeling software with an integrated game engine, which provides an easy to use and powerful set of tools for creating games.

The BLE_python_interface uses UDP socket communication between python and the blender game engine, and provides an api for passing images, game score, rewards and commands. Most of the functions present in ALE for example have been mirrored here.

The file ridge_game.blend is a simple blender game, where the player object has to go in a straight line on a narrow plank without falling. The longer the distance travelled, the higher the score. 
