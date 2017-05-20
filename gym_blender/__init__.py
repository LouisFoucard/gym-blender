from gym.envs.registration import register

register(
    id='ridge-v0',
    entry_point='gym_blender.envs:RidgeEnv',
)
