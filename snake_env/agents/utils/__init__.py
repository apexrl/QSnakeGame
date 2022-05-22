import datetime
import os
import pickle
import numpy as np

WIDTH = 40
LENGTH = 55
MAX_DIS = 48


def sigmoid(x):
    s = 1.0 / (1 + np.exp(-x))
    return s


def print_test(t, act, info):
    if act is None:
        return
    print("At time {}, using {} strategy: {}".format(t, info, act))


def save_rollouts(rollout_data):
    now = str(datetime.datetime.now()).replace(" ", "-").replace(":", "-")
    if not os.path.exists("data"):
        os.makedirs("data")
    with open(r"./data/{}.pkl".format(now), "wb") as f:
        pickle.dump(rollout_data, f)


def find_killable_players(num, gameInfo):
    # all_players = tableInfo['players'] # player list
    all_players = gameInfo["Player"]
    res = []
    for idx, player in enumerate(all_players):
        if idx == num:
            continue
        if player["IsDead"] and (not player["NowDead"]):
            continue
        if len(gameInfo["Map"]["SnakePosition"][idx]) == 0:
            continue
        res.append(idx)

    return res


def judge_siege(num, gameInfo):
    # 判断是否可以找到至少一个方向没有障碍

    # 自身头部位置
    PositionNow = gameInfo["Map"]["SnakePosition"][num][0]
    ActList = {"w": [0, 1], "s": [0, -1], "a": [-1, 0], "d": [1, 0]}

    PositionMove = None
    for i in ActList:
        Hit = 0
        PositionMove = list(np.sum([PositionNow, ActList[i]], axis=0))
        # 检查墙
        WallPosition_temp = np.array(gameInfo["Map"]["WallPosition"]).reshape(-1, 2)
        if ((WallPosition_temp == PositionMove).sum(axis=1) == 2).any():  # 有墙
            # print(i,"wall")
            Hit = 1
            continue
        for i_snake in range(len(gameInfo["Player"])):
            if gameInfo["Player"][i_snake]["IsDead"] and (
                not gameInfo["Player"][i_snake]["NowDead"]
            ):
                continue
            if len(gameInfo["Map"]["SnakePosition"][i_snake]) == 0:
                continue
            SnakePosition_temp = np.array(
                gameInfo["Map"]["SnakePosition"][i_snake]
            ).reshape(-1, 2)
            if (
                num == i_snake
                and np.sum((SnakePosition_temp == PositionMove).sum(axis=1) == 2) > 1
            ):  # 是自己，判断重叠是否大于1
                # print(i,"snake")
                Hit = 1
                continue
            if (
                num != i_snake
                and np.sum((SnakePosition_temp == PositionMove).sum(axis=1) == 2) > 0
            ):  # 是别人，判断重叠是否大于0
                # print(i,"snake")
                Hit = 1
                continue

    if Hit == 0:
        return False
    else:
        return True


def get_a_way(gameInfo, sta_pos, tar_poss):

    res = ""
    for tar_pos in tar_poss:
        delta = np.array(tar_pos) - np.array(sta_pos)
        # TODO: BFS 判断哪条路是通路，不通直接返回空，现在只判断第一个位置有没有重合默认返回先横着走再纵着走

        if delta[0] > 0:
            res += int(abs(delta[0])) * "a"

        if delta[0] < 0:
            res += int(abs(delta[0])) * "d"

        if delta[1] > 0:
            res += int(abs(delta[0])) * "s"

        if delta[1] < 0:
            res += int(abs(delta[0])) * "w"

        sta_pos = tar_pos

    return res


def position_in(pos, pos_candidate):
    pos = np.array(pos)
    pos_candidate = np.array(pos_candidate)

    res = np.sum((pos == pos_candidate).sum(axis=1) == 2)

    if res > 0:
        return True
    return False


def get_wall(gameInfo):
    return gameInfo["Map"]["WallPosition"]


def get_snakes(gameInfo):
    return gameInfo["Map"]["SnakePosition"]


def get_prop(gameInfo):
    return gameInfo["Map"]["PropPosition"]


def get_star(gameInfo):
    return gameInfo["Map"]["SugarPosition"]


def is_empty(pos, gameInfo):
    pos = np.array(pos).tolist()

    wall = get_wall(gameInfo)
    snake = get_snakes(gameInfo)

    if pos in wall:
        return False

    if pos in snake:
        return False

    return True


def get_empty(gameInfo):
    wall = get_wall(gameInfo)
    snake = get_snakes(gameInfo)
    prop = get_prop(gameInfo)

    res = []
    for i in range(1, LENGTH):
        for j in range(1, WIDTH):
            if [i, j] in wall:
                continue
            flag = False
            for snakepos in snake:
                if [i, j] in snakepos:
                    flag = True
                    break
            for proppos in prop:
                if [i, j] in proppos:
                    flag = True
                    break
            if flag:
                continue
            res.append([i, j])

    return res


def one_step_blocked(gameInfo, position, step):
    PositionNow = position
    ActList = {"w": [0, 1], "s": [0, -1], "a": [-1, 0], "d": [1, 0]}

    PositionMove = None

    PositionMove = list(np.sum([PositionNow, ActList[step]], axis=0))
    # 检查墙
    WallPosition_temp = np.array(gameInfo["Map"]["WallPosition"]).reshape(-1, 2)
    if ((WallPosition_temp == PositionMove).sum(axis=1) == 2).any():  # 有墙
        # print(i,"wall")
        return True
    Hit = 0
    for i_snake in range(len(gameInfo["Player"])):
        if gameInfo["Player"][i_snake]["IsDead"] and (
            not gameInfo["Player"][i_snake]["NowDead"]
        ):
            continue
        if len(gameInfo["Map"]["SnakePosition"][i_snake]) == 0:
            continue
        SnakePosition_temp = np.array(
            gameInfo["Map"]["SnakePosition"][i_snake]
        ).reshape(-1, 2)
        if np.sum((SnakePosition_temp == PositionMove).sum(axis=1) == 2) > 0:
            # print(i,"snake")
            Hit = 1
    if Hit == 0:
        # print(PositionMove)
        return False

    return True
