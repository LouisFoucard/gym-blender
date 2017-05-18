### Blender environment for gym

##### Description
Blender Learning Environment: BLE is a python interface for the blender game engine, to be added as a learning environment for Gym (https://github.com/openai/gym). Blender is a free 3D modeling software with an integrated game engine, which provides an easy to use and powerful set of tools for creating games. The main objective here is to provide an interface to the blender game engine, the games themselfeves can then be rather easily be designed in Blender. One can then generate custom virtual environments to tackle specific problems with reinforcement learning.

This interface for the blender game engine uses UDP socket communication between python and the game engine, and provides an api for passing images, game score, rewards and commands. Most of the functions present in ALE for example have been mirrored here.

The file ridge_game.blend is a simple blender game example, where the player object has to go in a straight line on a narrow plank without falling. The longer the distance travelled, the higher the score. 



##### Installation (Ubuntu 16.04):

- blender: 

```{r, engine='bash', count_lines}
sudo apt install blender
```
    

- ble-gym: 
    
```{r, engine='bash', count_lines}
git clone git@github.com:LouisFoucard/gym-blender.git
cd gym-blender
pip install -e .
    
```
   
Done!

##### Example:

run the random_example notebook to check installation. This is a simple random action agent to show most of the api.

