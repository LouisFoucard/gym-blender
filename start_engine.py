import bpy

bpy.context.scene.render.engine = 'BLENDER_GAME'
bpy.ops.view3d.game_start()
from bge import logic as GameLogic
GameLogic.startGame()