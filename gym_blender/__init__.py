from gym.envs.registration import register

register(
    id='blender-v0',
    entry_point='gym_blender.envs:BleEnv',
)
