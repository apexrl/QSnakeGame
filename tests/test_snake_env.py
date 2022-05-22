import time
from snake_env.core import SnakeEnv


def test_snake_env():
    env = SnakeEnv(visualize=True)
    obs = env.reset()
    for i in range(160):
        if i % 2 == 0:
            obs, rew, done, info = env.step(["w" for _ in range(env.player_num)])
        else:

            obs, rew, done, info = env.step(["s" for _ in range(env.player_num)])
        env.render()
        if done:
            print("done: ", done, i)
            break
        # time.sleep(0.5)
