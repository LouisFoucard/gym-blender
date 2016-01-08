# BLE_python_interface
Blender Learning Environment: inspired by the Arcade Learning Environment, BLE is a python interface for the blender game engine. Blender is a free 3D modeling software with an integrated game engine, which provides an easy to use and powerful set of tools for creating games. The aim of this work is to give deep q learning algorithms access a game engine which lets the user create its own custom games/scenarios.

The BLE_python_interface uses UDP socket communication between python and the blender game engine, and provides an api for passing images, game score, rewards and commands. Most of the functions present in ALE have been mirrored here.

The file ridge_game.blend is a simple blender game, where the player object has to go in a straight line on a narrow plank without falling. The longer the distance travelled, the higher the score. 
