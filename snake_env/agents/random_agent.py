from snake_env.agents.strategy import repeated_jump, random_strategy
from snake_env.agents.utils import LENGTH, WIDTH


class BaseAI:
    def __init__(self, strategy_map={}):
        self.strategy_map = strategy_map
        self.reset()

    def reset(self):
        self.last_steps = ""
        self.speed = 1
        self.prop = {"speed": 0, "strong": 0, "double": 0}  # 道具剩余时间
        self.length = 2
        self.save_length = 0

        self.inner_wall = 1  # 最内侧的墙在第几排, 初始化为1，有一个格子的冗余

        self.t = 0
        self.len_range = [1, LENGTH - 2]
        self.wid_range = [1, WIDTH - 2]

        self.total_wall_len = 0

    def update_status(self, num, gameInfo):

        self.save_length = gameInfo["Player"][num]["SaveLength"]
        self.length = len(gameInfo["Map"]["SnakePosition"][num])
        self.speed = gameInfo["Player"][num]["Speed"]

        self.prop.update(gameInfo["Player"][num]["Prop"])

        self.t = int(gameInfo["Map"]["Time"])
        wall_len_tmp = len(gameInfo["Map"]["WallPosition"])

        if self.t == 0:
            self.reset()

        # if (((self.t+1) >=5) and ((self.t+1) % 5 == 0)) or (self.t+1)>=100:
        # print("update status {}, {}".format(gameInfo["Map"]["Time"], np.sum((self.inner_wall == wall_position))))
        if wall_len_tmp > self.total_wall_len:  # 数目不一样说明缩圈了，否则则不计算
            self.inner_wall += 1
            self.total_wall_len = wall_len_tmp

        me_head = gameInfo["Map"]["SnakePosition"][num][0]

        self.len_range = [
            min(me_head[0], self.inner_wall + 1),
            max(me_head[0], LENGTH - self.inner_wall - 1),
        ]
        self.wid_range = [
            min(me_head[1], self.inner_wall + 1),
            max(me_head[1], WIDTH - self.inner_wall - 1),
        ]

        print(
            "At time {}, current range: {}, {}".format(
                self.t, self.len_range, self.wid_range
            )
        )

    def get_action(self, num, gameInfo, tableInfo):
        if len(gameInfo["Map"]["SnakePosition"][num]) == 0:  # 死了
            return "w"

        # simply return random_strategy
        act = random_strategy(num, gameInfo, tableInfo)
        if act is None:
            # simply return repeated_jump
            return repeated_jump(num, gameInfo, tableInfo)
        else:
            return act
