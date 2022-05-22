import numpy as np


def repeated_jump(num, gameInfo, tableInfo):
    # 示例
    if gameInfo["Player"][num]["IsDead"]:
        return "w"
    # 自身头部位置
    PositionHead = np.array(gameInfo["Map"]["SnakePosition"][num][0])
    # 自身第二个尾部位置
    PositionTail = np.array(gameInfo["Map"]["SnakePosition"][num][1])

    delta = PositionTail - PositionHead
    if delta[0] > 0:  # 蛇的姿态为<-
        return "d"
    elif delta[0] < 0:  # 蛇的姿态为->
        return "a"
    else:
        if delta[1] > 0:  # 蛇头向下
            return "w"
        elif delta[1] < 0:  # 蛇头向上
            return "s"
        if delta[1] > 0:  # 蛇头向上
            return "s"
        elif delta[1] < 0:  # 蛇头向下
            return "w"
