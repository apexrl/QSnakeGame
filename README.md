# QSnakeGame
Snake game RL environment for Ubiquant competition 2022.

We provide a gym-like interface for training RL agents.

Our state and reward design can be found in `ref/final_ai.py`.

Do not move the snake out of the map, such behaviors may cause the game error.

## Install dependency


```shell
conda install pybind11
pip instsall pyGame
```

## Use this env in python

Install the environment.

```shell
pip install -e .
```

Create env and step.

```python
from snake_env.core import SnakeEnv

env = SnakeEnv(visualize=True)
obs = env.reset()
for _ in range(10):
    obs, rew, done, info = env.step(["w" for _ in range(env.player_num)])
    env.render()
```
Or you can try our example with random agents.
```shell
pytest -s tests/test_built_in_ai.py
```

## Use in C++
Current cmake is only for building testing exec.

```shell
cd src
mkdir build & cd build
cmake ..
make
# play 50 rounds
./QSnakeEnv
# play 250 rounds 
./QSnakeEnv 0 250
# Add one human player
./QSnakeEnv 1 250
# play with fixed random seed
./QSnakeEnv 0 250 0
```
