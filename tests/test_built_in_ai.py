import os
import time
import pickle

from snake_env.core import SnakeEnv
from snake_env.agents import BaseAI


def test_agents():
    env = SnakeEnv(player_num=6, visualize=True)
    if not os.path.exists("obs_list.pkl"):
        agents = [BaseAI() for _ in range(env.player_num)]
        obs_list = []
        obs = env.reset()
        for _ in range(150):
            obs_list.append(obs)
            obs, rew, done, info = env.step(
                [
                    agent.get_action(idx, obs["gameinfo"], obs["tableinfo"])
                    for idx, agent in enumerate(agents)
                ]
            )
            if done:
                obs_list.append(obs)
                break

        pickle.dump(obs_list, open("obs_list.pkl", "wb"))

    with open("obs_list.pkl", "rb") as f:
        obs_list = pickle.load(f)

    for obs in obs_list:
        env.visualizer.render(obs)
        time.sleep(0.5)
