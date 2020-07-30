"""This is the script we can use to check our model. It was pulled (not forked) from
https://github.com/colinskow/move37 together with the dqn_basic script. I pulled the
script instead of forking since I did not need the full repository.

The move37 repository was originally forked from Forked from https://github.com/PacktPublishing/Deep-Reinforcement-Learning-Hands-On
"""

import gym
import time
import argparse
import numpy as np

import torch

from lib import wrappers
from lib import dqn_model
from lib.utils import mkdir

import collections

DEFAULT_ENV_NAME = "PongNoFrameskip-v4"
FPS = 25


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--model", required=True, help="Model file to load")
    parser.add_argument(
        "-e",
        "--env",
        default=DEFAULT_ENV_NAME,
        help="Environment name to use, default=" + DEFAULT_ENV_NAME,
    )
    parser.add_argument("-r", "--record", help="Directory to store video recording")
    parser.add_argument(
        "--no-visualize",
        default=True,
        action="store_false",
        dest="visualize",
        help="Disable visualization of the game play",
    )
    args = parser.parse_args()

    env = wrappers.make_env(args.env)
    if args.record:
        mkdir(".", args.record)
        env = gym.wrappers.Monitor(env, args.record)
    net = dqn_model.DQN(env.observation_space.shape, env.action_space.n)
    net.load_state_dict(
        torch.load(args.model, map_location=lambda storage, loc: storage)
    )

    state = env.reset()
    total_reward = 0.0
    c = collections.Counter()

    while True:
        start_ts = time.time()
        if args.visualize:
            env.render()
        state_v = torch.tensor(np.array([state], copy=False))
        q_vals = net(state_v).data.numpy()[0]
        action = np.argmax(q_vals)
        c[action] += 1
        state, reward, done, _ = env.step(action)
        total_reward += reward
        if done:
            break
        if args.visualize:
            delta = 1 / FPS - (time.time() - start_ts)
            if delta > 0:
                time.sleep(delta)
    print("Total reward: %.2f" % total_reward)
    print("Action counts:", c)
    if args.record:
        env.env.close()