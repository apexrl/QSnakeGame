import collections
import copy
import gym

import numpy as np

N_SNAKE = 6
N_CH = 60

CH_SUGAR = 0
CH_WALL = 1
CH_SPEED = 2
CH_POWER = 3
CH_DOUBLE = 4
CH_MY_SNAKE_POS = 5  # with len info integrated
CH_MY_HEADS_POS = 6  # with len info integrated
CH_MY_BODIES_POS = 7  # with len info integrated
CH_OTHER1_POS = 8  # with len info integrated
CH_OTHER2_POS = 9
CH_OTHER3_POS = 10
CH_OTHER4_POS = 11
CH_OTHER5_POS = 12
CH_MY_POSSIBLE_HEADS = 13  # info about steps left from current micro step
CH_OTHER1_POSSIBLE_HEADS = 14  # integrate speed info
CH_OTHER2_POSSIBLE_HEADS = 15
CH_OTHER3_POSSIBLE_HEADS = 16
CH_OTHER4_POSSIBLE_HEADS = 17
CH_OTHER5_POSSIBLE_HEADS = 18
CH_ALL_POWER = 19  # replaced all snakes' position by their own power time left
CH_ALL_SPEED = 20  # replaced all snakes' position by their own speed time left
CH_ALL_DOUBLE = 21  # replaced all snakes' position by their own double time left
CH_MY_POSSIBLE_HEADS_POWER = 22  # replaced by power
CH_OTHER1_POSSIBLE_HEADS_POWER = 23  # replaced by power
CH_OTHER2_POSSIBLE_HEADS_POWER = 24
CH_OTHER3_POSSIBLE_HEADS_POWER = 25
CH_OTHER4_POSSIBLE_HEADS_POWER = 26
CH_OTHER5_POSSIBLE_HEADS_POWER = 27
CH_OTHERS_KILLABLE = 28
CH_OTHERS_KILLABLE_F = 29
CH_OTHER1_POSSIBLE_HEADS_KILLABLE = 30  # replaced by killable
CH_OTHER2_POSSIBLE_HEADS_KILLABLE = 31
CH_OTHER3_POSSIBLE_HEADS_KILLABLE = 32
CH_OTHER4_POSSIBLE_HEADS_KILLABLE = 33
CH_OTHER5_POSSIBLE_HEADS_KILLABLE = 34
CH_OTHER1_POSSIBLE_HEADS_KILLABLE_F = 35  # replaced by killable_f
CH_OTHER2_POSSIBLE_HEADS_KILLABLE_F = 36
CH_OTHER3_POSSIBLE_HEADS_KILLABLE_F = 37
CH_OTHER4_POSSIBLE_HEADS_KILLABLE_F = 38
CH_OTHER5_POSSIBLE_HEADS_KILLABLE_F = 39
CH_ALL_SCORE_LEN = 40
CH_ALL_SCORE_KILL = 41
CH_LEFT_LEN_IF_HIT = 42
CH_LEFT_LEN_IF_NO_HIT = 43
CH_ALL_FRONTS = 44
CH_ALL_SAVE_LEN = 45
CH_IN_ROUND_PROGRESS = 46  # progress is defined as `num_steps_taken/my_speed`
CH_NEXT_WALL_POS = 47
CH_MY_LAST_POS = 48
CH_OTHER1_LAST_POS = 49
CH_OTHER2_LAST_POS = 50
CH_OTHER3_LAST_POS = 51
CH_OTHER4_LAST_POS = 52
CH_OTHER5_LAST_POS = 53
CH_MY_PREV_ACT = 54
CH_OTHER1_PREV_ACT = 55
CH_OTHER2_PREV_ACT = 56
CH_OTHER3_PREV_ACT = 57
CH_OTHER4_PREV_ACT = 58
CH_OTHER5_PREV_ACT = 59


class RewardWrapper(gym.Wrapper):
    def __init__(self, env):
        super().__init__(env)
        self.last_obs = None
        self._cumulative_reward = None

    def reset(self, **kwargs):
        state = self.env.reset(**kwargs)
        self.last_obs = copy.deepcopy(self.obs)
        return state

    def step(self, action):
        state, _, done, info = self.env.step(action)
        if self.obs['gameinfo']['Map']['Time'] == self.last_obs['gameinfo']['Map']['Time']:  # skip micro step
            return state, 0., done, info

        my_last_info = self.last_obs['gameinfo']['Player'][self.controlled_player_idx]
        my_curr_info = self.obs['gameinfo']['Player'][self.controlled_player_idx]
        is_dead = my_curr_info['IsDead']
        n_curr_alive_player = sum([not player['IsDead'] for player in self.obs['gameinfo']['Player']])

        last_len = my_last_info['Score_len']
        curr_len = my_curr_info['Score_len']
        rew_len = (curr_len - last_len) * 0.05

        last_kill = my_last_info['Kill']
        curr_kill = my_curr_info['Kill']
        rew_kill = (curr_kill - last_kill) * 0.7 if last_kill == 0 else (curr_kill - last_kill) * 0.2

        last_speed = my_last_info['Speed']
        curr_speed = my_curr_info['Speed']
        if not is_dead:
            if curr_speed > last_speed:
                rew_speed = (curr_speed - last_speed) * 0.02
            elif curr_speed == 0 and last_speed > 0:
                rew_speed = min(-0.01 * last_speed, -0.05)  # lost all speed
            else:
                rew_speed = 0.
        else:
            rew_speed = 0.

        last_strong = my_last_info['Prop']['strong']
        curr_strong = my_curr_info['Prop']['strong']
        if not is_dead and curr_strong > last_strong:
            rew_strong = (curr_strong - last_strong) * 0.06 / 5.
        else:
            rew_strong = 0.

        last_double = my_last_info['Prop']['double']
        curr_double = my_curr_info['Prop']['double']
        if not is_dead and curr_double > last_double:
            rew_double = (curr_double - last_double) * 0.04 / 5.
        else:
            rew_double = 0.

        last_time = int(self.last_obs['gameinfo']['Map']['Time'])
        curr_time = int(self.obs['gameinfo']['Map']['Time'])
        rew_time = (curr_time - last_time) * 0.01 if not my_curr_info['IsDead'] and n_curr_alive_player > 1 else 0

        curr_score = my_curr_info['Score']
        curr_other_score_max = np.mean([self.obs['gameinfo']['Player'][i]['Score'] for i in range(N_SNAKE) if i != self.controlled_player_idx])
        curr_adv = curr_score - curr_other_score_max
        last_score = my_last_info['Score']
        last_other_score_max = np.mean([self.obs['gameinfo']['Player'][i]['Score'] for i in range(N_SNAKE) if i != self.controlled_player_idx])
        last_adv = last_score - last_other_score_max
        rew_score = (curr_adv - last_adv) * 5.0

        # more reward for early stage
        curr_time = my_curr_info['Score_time']
        if curr_time < 10:
            rew_speed *= 3
            rew_strong *= 2
            rew_double *= 2
        elif curr_time < 20:
            rew_speed *= 2
            rew_strong *= 2
            rew_double *= 2
        elif curr_time < 30:
            rew_speed *= 1.5
            rew_strong *= 1.5
            rew_double *= 1.5

        reward = rew_len + rew_kill + rew_speed + rew_strong + rew_double + rew_time + rew_score
        self.last_obs = copy.deepcopy(self.obs)

        return state, reward, done, info


class Converter:
    def __init__(self):
        self.obs = None
        self.player_name = None
        self._inner_steps_left = None  # 该回合的剩余步数
        self._round_action = None  # 该回合的action str，每次infer会出一个micro action暂存在后面
        self._last_micro_action = None

        self._my_front_pos = None  # 当前小步下控制的最前面的那个一格head
        self._my_heads_pos = None  # 该回合中截止到当前小步所有head的位置
        self._my_bodies_pos = None  # 该回合中截止到当前小步所有body的位置
        self._in_round_save_len = None  # 该回合中截止到当前小步save length的值
        self._last_snakes_pos = None  # 所有蛇上一回合的位置
        self._last_5_act_len = None  # 所有蛇过去三回合的移动步数

    def reset(self, init_obs, player_name):
        init_obs = preprocess_obs(init_obs)
        self.obs = init_obs
        self.player_name = player_name
        self._inner_steps_left = self.get_player_info_by_name(self.obs, self.player_name)['Speed']
        self._round_action = ''
        self._last_micro_action = ''
        self._last_snakes_pos = init_obs['gameinfo']['Map']['SnakePosition']  # the same with current pos for the first round
        self._last_5_act_len = [collections.deque([0] * 5, maxlen=5) for _ in range(N_SNAKE)]

    @staticmethod
    def get_player_info_by_name(obs, player_name):
        for player_info in obs['gameinfo']['Player']:
            if player_info['Name'] == player_name:
                return player_info
        else:
            raise ValueError(f'No player with name "{player_name}".')

    @staticmethod
    def get_kill_info(game_info, move_num, main_id):
        """
        Return infos which help killing.

        :param game_info:
        :param move_num: length of actions took in current step.
        :param main_id: id of current player
        :return:
        """
        for i in range(N_SNAKE):
            game_info["Player"][i]["Length"] = len(game_info['Map']['SnakePosition'][i])

        num = len(game_info["Player"])
        final_length = [0] * num
        for i in range(num):
            if i == main_id:
                final_length[i] = min(move_num, game_info["Player"][i]["SaveLength"]) + game_info["Player"][i]["Length"]
            elif game_info["Player"][i]["IsDead"] or game_info["Player"][i]["NowDead"]:
                final_length[i] = 0
            else:
                final_length[i] = min(game_info["Player"][i]["SaveLength"], game_info["Player"][i]["Speed"]) + game_info["Player"][i]["Length"]
        # if can kill the opponent in current
        killable = []
        # if can kill the opponent with continuous attack
        killable_f = []
        has_strong = (game_info["Player"][main_id]["Prop"]["strong"] > 1)

        left_length_if_no_hit = final_length[main_id] / game_info["Player"][main_id]["Length"]

        if has_strong:
            left_length_if_hit = max(0, final_length[main_id] - move_num) / game_info["Player"][main_id]["Length"]
        else:
            left_length_if_hit = 0

        for i in range(num):
            if i == main_id:
                continue
            if game_info["Player"][i]["IsDead"] or game_info["Player"][i]["NowDead"]:
                killable.append(False)
                killable_f.append(False)
                continue

            oppo_has_strong = (game_info["Player"][i]["Prop"]["strong"] > 1)
            if not has_strong and not oppo_has_strong:
                killable.append(final_length[main_id] > final_length[i])
                killable_f.append(final_length[main_id] > final_length[i])
                # left_length_if_hit.append(1. if final_length[main_id] > final_length[i] else 0.)
            elif not has_strong and oppo_has_strong:
                killable.append(False)
                killable_f.append(False)
            elif has_strong and not oppo_has_strong:
                killable.append(True)
                killable_f.append(True)
                # left_length_if_hit.append()
            elif has_strong and oppo_has_strong:
                killable.append(False)
                main_value = min(game_info["Player"][main_id]["Prop"]["strong"],
                                 (game_info["Player"][main_id]["Length"] + game_info["Player"][main_id]["SaveLength"]) / max(1, move_num))
                oppo_value = min(game_info["Player"][i]["Prop"]["strong"],
                                 game_info["Player"][i]["Length"] + game_info["Player"][i]["SaveLength"], )
                killable_f.append(main_value > oppo_value)

        return killable, killable_f, left_length_if_no_hit, left_length_if_hit

    def convert_state(self, obs, ban_wall_walk=True):
        obs = preprocess_obs(obs)
        self.obs = obs

        map_info = obs['gameinfo']['Map']
        player_infos = obs['gameinfo']['Player']
        player_names = obs['tableinfo']['players']
        map_len, map_wid = map_info['Length'], map_info['Width']
        my_player_idx = player_names.index(self.player_name)

        sugar_pos = np.array(map_info['SugarPosition'])
        wall_pos = np.array(map_info['WallPosition'])
        speed_pos = np.array(map_info['PropPosition'][0])
        power_pos = np.array(map_info['PropPosition'][1])
        double_pos = np.array(map_info['PropPosition'][2])
        snakes_pos = [np.array(map_info['SnakePosition'][i]) for i in range(N_SNAKE)]
        my_save_len = player_infos[my_player_idx]['SaveLength']
        my_snake_pos = np.array(map_info['SnakePosition'][my_player_idx] if my_save_len > 0 else map_info['SnakePosition'][my_player_idx][:-1])  # keep the last body only if save_len > 0
        my_snake_last_pos = np.array(self._last_snakes_pos[my_player_idx])
        my_start_front = np.array(map_info['SnakePosition'][my_player_idx][0])  # 回合开始时我的头
        my_prev_act = player_infos[my_player_idx]['Act']

        other_snakes_idx = [i for i in range(N_SNAKE) if i != my_player_idx]
        other_snakes_pos = [np.array(map_info['SnakePosition'][i]) for i in other_snakes_idx]
        other_snakes_last_pos = [np.array(self._last_snakes_pos[i]) for i in other_snakes_idx]
        other_snakes_order = np.argsort([len(pos) for pos in other_snakes_pos])[::-1]  # player idx of the longest snake, of 2nd, ...
        other_snakes_idx = [other_snakes_idx[i] for i in other_snakes_order]  # reorder w.r.t. length
        other_snakes_save_len = [player_infos[i]['SaveLength'] for i in other_snakes_idx]
        other_snakes_pos = [other_snakes_pos[i] for i in other_snakes_order]  # reorder w.r.t. length
        other_snakes_pos = [pos if save_len > 0 else pos[:-1] for pos, save_len in zip(other_snakes_pos, other_snakes_save_len)]  # keep the last body only if save_len > 0
        other_snakes_last_pos = [other_snakes_last_pos[i] for i in other_snakes_order]  # reorder w.r.t. length
        others_prop_speed = [max(player_infos[i]['Prop']['speed'] - 1, 0) for i in other_snakes_idx]
        others_prop_power = [max(player_infos[i]['Prop']['strong'] - 1, 0) for i in other_snakes_idx]
        others_prop_double = [max(player_infos[i]['Prop']['double'] - 1, 0) for i in other_snakes_idx]
        other_snakes_act = [player_infos[i]['Act'] for i in other_snakes_idx]
        other_snakes_speed = [player_infos[i]['Speed'] for i in other_snakes_idx]
        other_snakes_score_len = [player_infos[i]['Score_len'] for i in other_snakes_idx]
        other_snakes_score_kill = [player_infos[i]['Score_kill'] for i in other_snakes_idx]
        other_snakes_front = [pos[0] if len(pos) > 0 else None for pos in other_snakes_pos]  # 回合开始时对方的头
        my_score_len = player_infos[my_player_idx]['Score_len']
        my_score_kill = player_infos[my_player_idx]['Score_kill']
        my_prop_speed = max(player_infos[my_player_idx]['Prop']['speed'] - 1, 0)
        my_prop_power = max(player_infos[my_player_idx]['Prop']['strong'] - 1, 0)
        my_prop_double = max(player_infos[my_player_idx]['Prop']['double'] - 1, 0)
        my_speed = player_infos[my_player_idx]['Speed']
        my_len = len(map_info['SnakePosition'][my_player_idx])

        if len(self._round_action) == 0:
            for q, player_info in zip(self._last_5_act_len, player_infos):
                q.append(len(player_info['Act']) if player_info['Act'] is not None else 0)
        my_last_5_act_len = self._last_5_act_len[my_player_idx]
        others_last_5_act_len = [self._last_5_act_len[i] for i in other_snakes_idx]

        killable, killable_f, left_length_if_no_hit, left_length_if_hit = \
            self.get_kill_info(obs['gameinfo'], move_num=len(self._round_action), main_id=my_player_idx)
        killable = [killable[i] for i in other_snakes_order]  # reorder w.r.t. length
        killable_f = [killable_f[i] for i in other_snakes_order]  # reorder w.r.t. length

        # maintain in-round states
        if len(self._round_action) == 0:
            self._inner_steps_left = self.get_player_info_by_name(self.obs, self.player_name)['Speed']
            self._my_front_pos = np.array(map_info['SnakePosition'][my_player_idx][0])
            self._my_heads_pos = collections.deque()
            self._my_bodies_pos = collections.deque(copy.deepcopy(map_info['SnakePosition'][my_player_idx]))
            self._in_round_save_len = player_infos[my_player_idx]['SaveLength']
            if self._in_round_save_len == 0:
                self._my_bodies_pos.pop()
        else:
            if self._last_micro_action in ['w', 'a', 's', 'd']:
                if self._last_micro_action == 'w':
                    self._my_front_pos[1] = self._my_front_pos[1] + 1
                elif self._last_micro_action == 'a':
                    self._my_front_pos[0] = self._my_front_pos[0] - 1
                elif self._last_micro_action == 's':
                    self._my_front_pos[1] = self._my_front_pos[1] - 1
                elif self._last_micro_action == 'd':
                    self._my_front_pos[0] = self._my_front_pos[0] + 1
                self._my_heads_pos.appendleft(copy.deepcopy(self._my_front_pos))
                if self._in_round_save_len == 0:
                    if len(self._my_bodies_pos) > 0:
                        self._my_bodies_pos.pop()
                    else:
                        self._my_heads_pos.pop()
                else:
                    self._in_round_save_len -= 1
            elif self._last_micro_action == 'reverse':
                self._my_front_pos = np.array(map_info['SnakePosition'][my_player_idx][-1])
                self._my_heads_pos = collections.deque(reversed(copy.deepcopy(map_info['SnakePosition'][my_player_idx][1:])))
                self._my_bodies_pos = collections.deque(copy.deepcopy(map_info['SnakePosition'][my_player_idx][0:1]))
                # self._in_round_save_len 无需修改，因为只让其为0时才允许高阶横跳
            else:
                raise ValueError("Unexpected micro action's type:", self._last_micro_action)

        def mark_point(arr_2d, index_arr, check_in_map=False, with_order=False):
            index_arr = np.asarray(index_arr)
            if check_in_map and len(index_arr) > 0:
                index_arr[:, 0] = np.clip(index_arr[:, 0], 0, map_len - 1)
                index_arr[:, 1] = np.clip(index_arr[:, 1], 0, map_wid - 1)
            if not with_order:
                if index_arr.size > 0:  # ignore empty arr
                    arr_2d[index_arr[:, 0], index_arr[:, 1]] = 1
            else:
                for i, (x, y) in enumerate(reversed(index_arr)):
                    arr_2d[x, y] = (i + 1) / 100.  # 除以固定数值以体现绝对长度值

        img = np.zeros((N_CH, map_len, map_wid))
        mark_point(img[CH_SUGAR], sugar_pos)
        mark_point(img[CH_WALL], wall_pos)
        mark_point(img[CH_SPEED], speed_pos)
        mark_point(img[CH_POWER], power_pos)
        mark_point(img[CH_DOUBLE], double_pos)
        mark_point(img[CH_MY_SNAKE_POS], my_snake_pos, with_order=True)
        mark_point(img[CH_MY_HEADS_POS], self._my_heads_pos, check_in_map=True, with_order=True)
        mark_point(img[CH_MY_BODIES_POS], self._my_bodies_pos, check_in_map=True, with_order=True)
        mark_point(img[CH_OTHER1_POS], other_snakes_pos[0], with_order=True)  # pos of the 1st longest snake
        mark_point(img[CH_OTHER2_POS], other_snakes_pos[1], with_order=True)  # pos of the 2nd longest snake
        mark_point(img[CH_OTHER3_POS], other_snakes_pos[2], with_order=True)  # ...
        mark_point(img[CH_OTHER4_POS], other_snakes_pos[3], with_order=True)
        mark_point(img[CH_OTHER5_POS], other_snakes_pos[4], with_order=True)
        mark_point(img[CH_MY_LAST_POS], my_snake_last_pos, with_order=True)  # past info
        mark_point(img[CH_OTHER1_LAST_POS], other_snakes_last_pos[0], with_order=True)  # others' past info, aligned with current order
        mark_point(img[CH_OTHER2_LAST_POS], other_snakes_last_pos[1], with_order=True)
        mark_point(img[CH_OTHER3_LAST_POS], other_snakes_last_pos[2], with_order=True)
        mark_point(img[CH_OTHER4_LAST_POS], other_snakes_last_pos[3], with_order=True)
        mark_point(img[CH_OTHER5_LAST_POS], other_snakes_last_pos[4], with_order=True)
        mark_point(img[CH_ALL_FRONTS], [self._my_front_pos] + [f for f in other_snakes_front if f is not None])  # pos of the fronts of all snakes
        img[CH_IN_ROUND_PROGRESS] = np.ones((map_len, map_wid)) * len(self._round_action) / my_speed

        if len(self._round_action) == 0:
            self._last_snakes_pos = map_info['SnakePosition']

        def mark_possible_heads(channel_id, steps_left, front_pos):
            """标记随距离递减的可达区域，对手从回合开始计，自己从当前小步开始计"""
            tmp_x = np.tile(np.arange(map_len), (map_wid, 1)).transpose((1, 0)) - front_pos[0]
            tmp_y = np.tile(np.arange(map_wid), (map_len, 1)) - front_pos[1]
            # value of each point denotes the num available steps left when reaching this point,
            # and +1 for denoting the most far away point can be reached
            steps_left_to_target = np.clip(steps_left - (abs(tmp_x) + abs(tmp_y)) + 1, 0, 999999)
            steps_left_to_target[front_pos[0], front_pos[1]] -= 2  # special case for current position
            img[channel_id] = steps_left_to_target / max(steps_left, 1)  # rescale

        def log_mapping(value):
            """将较小的数值映射到更大的区间内"""
            return np.log(1 + value) / 3.

        # integrate speed info into channel
        mark_possible_heads(CH_MY_POSSIBLE_HEADS, steps_left=my_speed-len(self._round_action), front_pos=self._my_front_pos)
        for i in range(N_SNAKE - 1):
            if other_snakes_front[i] is not None:
                i_ch = [CH_OTHER1_POSSIBLE_HEADS, CH_OTHER2_POSSIBLE_HEADS, CH_OTHER3_POSSIBLE_HEADS, CH_OTHER4_POSSIBLE_HEADS, CH_OTHER5_POSSIBLE_HEADS][i]
                oppo_speed = other_snakes_speed[i]
                oppo_front_pos = other_snakes_front[i]
                mark_possible_heads(i_ch, steps_left=oppo_speed, front_pos=oppo_front_pos)

        # mark with power, reflect the difficulty to kill the target snake
        for i_ch_origin, speed, power, double in \
                zip([CH_MY_SNAKE_POS, CH_OTHER1_POS, CH_OTHER2_POS, CH_OTHER3_POS, CH_OTHER4_POS, CH_OTHER5_POS],
                    [my_prop_speed, *others_prop_speed],
                    [my_prop_power, *others_prop_power],
                    [my_prop_double, *others_prop_double]):
            img[CH_ALL_SPEED][img[i_ch_origin] > 0] = log_mapping(speed)
            img[CH_ALL_POWER][img[i_ch_origin] > 0] = log_mapping(power)
            img[CH_ALL_DOUBLE][img[i_ch_origin] > 0] = log_mapping(double)
        img[CH_MY_POSSIBLE_HEADS_POWER][img[CH_MY_POSSIBLE_HEADS] > 0] = log_mapping(my_prop_power)
        for (i_ch_origin, i_ch_power), power in \
                zip([(CH_OTHER1_POSSIBLE_HEADS, CH_OTHER1_POSSIBLE_HEADS_POWER),
                     (CH_OTHER2_POSSIBLE_HEADS, CH_OTHER2_POSSIBLE_HEADS_POWER),
                     (CH_OTHER3_POSSIBLE_HEADS, CH_OTHER3_POSSIBLE_HEADS_POWER),
                     (CH_OTHER4_POSSIBLE_HEADS, CH_OTHER4_POSSIBLE_HEADS_POWER),
                     (CH_OTHER5_POSSIBLE_HEADS, CH_OTHER5_POSSIBLE_HEADS_POWER)],
                    others_prop_power):
            img[i_ch_power][img[i_ch_origin] > 0] = log_mapping(power)

        # mark with score_len & score_kill & save_len
        for i_ch_origin, score_len, score_kill, save_len in \
                zip([CH_MY_SNAKE_POS, CH_OTHER1_POS, CH_OTHER2_POS, CH_OTHER3_POS, CH_OTHER4_POS, CH_OTHER5_POS],
                    [my_score_len, *other_snakes_score_len],
                    [my_score_kill, *other_snakes_score_kill],
                    [my_save_len, *other_snakes_save_len]):
            img[CH_ALL_SCORE_LEN][img[i_ch_origin] > 0] = score_len / 6.
            img[CH_ALL_SCORE_KILL][img[i_ch_origin] > 0] = score_kill / 6.
            img[CH_ALL_SAVE_LEN][img[i_ch_origin] > 0] = min(1., save_len / 10.)

        # mark killable info
        for i_ch_origin, k1, k2 in \
                zip([CH_OTHER1_POS, CH_OTHER2_POS, CH_OTHER3_POS, CH_OTHER4_POS, CH_OTHER5_POS], killable, killable_f):
            img[CH_OTHERS_KILLABLE][img[i_ch_origin] > 0] = float(k1)
            img[CH_OTHERS_KILLABLE_F][img[i_ch_origin] > 0] = float(k2)
        for (i_ch_origin, i_ch_k1, i_ch_k2), k1, k2 in \
                zip([(CH_OTHER1_POSSIBLE_HEADS, CH_OTHER1_POSSIBLE_HEADS_KILLABLE, CH_OTHER1_POSSIBLE_HEADS_KILLABLE_F),
                     (CH_OTHER2_POSSIBLE_HEADS, CH_OTHER2_POSSIBLE_HEADS_KILLABLE, CH_OTHER2_POSSIBLE_HEADS_KILLABLE_F),
                     (CH_OTHER3_POSSIBLE_HEADS, CH_OTHER3_POSSIBLE_HEADS_KILLABLE, CH_OTHER3_POSSIBLE_HEADS_KILLABLE_F),
                     (CH_OTHER4_POSSIBLE_HEADS, CH_OTHER4_POSSIBLE_HEADS_KILLABLE, CH_OTHER4_POSSIBLE_HEADS_KILLABLE_F),
                     (CH_OTHER5_POSSIBLE_HEADS, CH_OTHER5_POSSIBLE_HEADS_KILLABLE, CH_OTHER5_POSSIBLE_HEADS_KILLABLE_F)],
                    killable, killable_f):
            img[i_ch_k1][img[i_ch_origin] > 0] = float(k1)
            img[i_ch_k2][img[i_ch_origin] > 0] = float(k2)
        img[CH_LEFT_LEN_IF_HIT] = np.ones((map_len, map_wid)) * left_length_if_hit
        img[CH_LEFT_LEN_IF_NO_HIT] = np.ones((map_len, map_wid)) * left_length_if_no_hit

        # extract curr time's wall thickness and next time's wall position
        indent = 0  # thickness of wall circle
        while indent < map_wid-indent:
            if np.sum(img[CH_WALL][indent:map_len-indent, indent:map_wid-indent]) == 0:
                break
            indent += 1
        reduce_flag = 0  # 下一时刻是否缩圈
        if (int(map_info['Time']) + 1) % 5 == 0:
            if (int(map_info['Time']) + 1) >= 100 or map_len * map_wid - np.sum(img[CH_WALL] + img[CH_SUGAR]) >= 400:
                reduce_flag = 1
                # infer next round's possible wall pos
                img[CH_NEXT_WALL_POS][indent:map_len-indent, indent:map_wid-indent] = 1
                img[CH_NEXT_WALL_POS][indent+1:map_len-indent-1, indent+1:map_wid-indent-1] = 0

        def mark_points_of_prev_act(snake_front, snake_act, ch_idx):
            if snake_act is None or snake_front is None:
                return
            mapping = {'w': [0, 1], 'a': [-1, 0], 's': [0, -1], 'd': [1, 0]}
            tmp_front = copy.deepcopy(snake_front)
            arr = [snake_front]
            for per_act in snake_act[-1::-1]:
                tmp_front -= mapping[per_act]
                arr.append(copy.deepcopy(tmp_front))
            mark_point(img[ch_idx], arr, check_in_map=True, with_order=True)

        mark_points_of_prev_act(my_start_front, my_prev_act, CH_MY_PREV_ACT)
        mark_points_of_prev_act(other_snakes_front[0], other_snakes_act[0], CH_OTHER1_PREV_ACT)
        mark_points_of_prev_act(other_snakes_front[1], other_snakes_act[1], CH_OTHER2_PREV_ACT)
        mark_points_of_prev_act(other_snakes_front[2], other_snakes_act[2], CH_OTHER3_PREV_ACT)
        mark_points_of_prev_act(other_snakes_front[3], other_snakes_act[3], CH_OTHER4_PREV_ACT)
        mark_points_of_prev_act(other_snakes_front[4], other_snakes_act[4], CH_OTHER5_PREV_ACT)

        front_margin = np.array([
            self._my_front_pos[0], map_len - self._my_front_pos[0],
            self._my_front_pos[1], map_wid - self._my_front_pos[1],
        ])
        past_time = int(map_info['Time'])
        n_curr_alive_player = sum([not player['IsDead'] for player in player_infos])
        progress_multihot = multihot(num_feat=10, idx=int(past_time / 150. * 10) + 1)
        len_diff_to_max = (player_infos[my_player_idx]['Score_len_origin'] - max([player_infos[i]['Score_len_origin'] for i in range(N_SNAKE)]))
        killnum_diff_to_max = (player_infos[my_player_idx]['Score_kill_origin'] - max([player_infos[i]['Score_kill_origin'] for i in range(N_SNAKE)]))

        def extract_per_player_info(player_info, snake_pos, last_5_act_len):
            alive = not player_info['IsDead']
            basic_arr = np.array([
                alive,
                player_info['Speed'] / 100. if alive else 0.,
                player_info['Kill'] / 5.,
                player_info['SaveLength'] / 20. if alive else 0.,
                player_info['Prop']['speed'] / 200. if alive else 0.,
                player_info['Prop']['strong'] / 50. if alive else 0.,
                player_info['Prop']['double'] / 50. if alive else 0.,
                player_info['Score_len'] / 6.,
                player_info['Score_kill'] / 6.,
                player_info['Score_time'] / 6.,
                player_info['Score_len_origin'] / 100.,
                player_info['Score_kill_origin'] / 10.,
                player_info['Score_time_origin'] / 150.,
                player_info['Score'] / 6.,
                len(snake_pos) / 100. if alive else 0.,
            ])
            if alive and (player_info['LastAct'] is None or len(player_info['LastAct']) == 0):
                last_act_arr = np.zeros((4,))
            else:
                last_act_arr = onehot(4, 'wasd'.index(player_info['LastAct']))
            last_5_act_len_arr = np.array(last_5_act_len) / 50. if alive else np.zeros((5,))
            arr = np.concatenate([basic_arr, last_act_arr, last_5_act_len_arr])
            return arr

        arr_me = extract_per_player_info(player_infos[my_player_idx], my_snake_pos, my_last_5_act_len)
        arr_others = []
        for other_idx, other_pos, other_last_5_act_len in zip(other_snakes_idx, other_snakes_pos, others_last_5_act_len):
            arr_others.append(extract_per_player_info(player_infos[other_idx], other_pos, other_last_5_act_len))

        mlp_input = np.concatenate([
            front_margin / map_len,
            [past_time / 150.],
            [n_curr_alive_player / 6.],
            progress_multihot,
            [len_diff_to_max / 100., killnum_diff_to_max / 10.],
            arr_me,
            *arr_others,
            [indent * 2 / map_wid, reduce_flag],
        ])

        def shortest_path(p0, p_target):
            """p0是出发点，p_target是目标点，返回走到p_target的最短路径，可以撞墙。"""
            x_diff = p_target[0] - p0[0]
            y_diff = p_target[1] - p0[1]
            path = ''
            if x_diff > 0:
                path += 'd' * x_diff
            if x_diff < 0:
                path += 'a' * abs(x_diff)
            if y_diff > 0:
                path += 'w' * y_diff
            if y_diff < 0:
                path += 's' * abs(y_diff)
            return path

        def shortest_path_consider_wall(p0, p_target):
            """p0是出发点，p_target是目标点，返回走到p_target的最短路径，不可以撞墙。"""

            def p_hash(point):
                return int(point[0] * 100 + point[1])

            mapping = {'w': [0, 1], 'a': [-1, 0], 's': [0, -1], 'd': [1, 0]}
            queue = collections.deque([p0])
            hist = {p_hash(p0): ''}
            path = ''
            while len(path) == 0 and len(queue) > 0:
                p = queue.popleft()
                prefix = hist[p_hash(p)]
                for move in mapping:
                    p_next = p + mapping[move]
                    if p_hash(p_next) not in hist and img[CH_WALL][p_next[0], p_next[1]] != 1:
                        if abs(p_next[0] - p_target[0]) + abs(p_next[1] - p_target[1]) == 0:
                            path = prefix + move
                            break
                        hist[p_hash(p_next)] = prefix + move
                        queue.append(p_next)
            return path

        kill_path = ''
        if len(self._round_action) == 0 and (int(map_info['Time']) > 40 or my_len > 40):
            other_alive_players_idx = [i for i in range(N_SNAKE) if not player_infos[i]['IsDead'] and i != my_player_idx]
            other_alive_player_power_prop = [player_infos[i]['Prop']['strong'] for i in other_alive_players_idx]
            others_killable = [power_prop <= 1 for power_prop in other_alive_player_power_prop]
            other_alive_players_front = [snakes_pos[i][0] for i in other_alive_players_idx]
            others_achievable = [img[CH_MY_POSSIBLE_HEADS][front[0], front[1]] > 0 for front in other_alive_players_front]
            force_killable = [k and a for k, a in zip(others_killable, others_achievable)]  # 其他人能不能被穿墙杀
            if any(force_killable) and my_prop_power > 1:
                target_idx = other_alive_players_idx[force_killable.index(True)]
                target_front = snakes_pos[target_idx][0]
                target_last_act = player_infos[target_idx]['LastAct']
                # dist = abs(self._my_front_pos[0] - target_front[0]) + abs(self._my_front_pos[1] - target_front[1])
                kill_path = shortest_path_consider_wall(self._my_front_pos, target_front)  # 杀人辅助路径1，不撞墙的最短路径
                if kill_path == '' and n_curr_alive_player == 2:
                    kill_path = shortest_path(self._my_front_pos, target_front)  # 杀人辅助路径2，可能撞墙的最短直角路径

                # 封杀对手所有行动方向
                if kill_path != '':
                    counter_act_map = {'a': 'd', 'd': 'a', 'w': 's', 's': 'w'}
                    dir_map = {'w': [0, 1], 'a': [-1, 0], 's': [0, -1], 'd': [1, 0]}
                    remain_dir = {'w', 'a', 's', 'd'}
                    remain_dir.remove(counter_act_map[kill_path[-1]])
                    if target_last_act in remain_dir:  # 最先封杀上次行动方向
                        next_pos = target_front + dir_map[target_last_act]
                        if img[CH_WALL][next_pos[0], next_pos[1]] != 1:  # 不会撞墙
                            kill_path += target_last_act
                            kill_path += counter_act_map[target_last_act]
                        remain_dir.remove(target_last_act)
                    for d in remain_dir:
                        next_pos = target_front + dir_map[d]
                        if img[CH_WALL][next_pos[0], next_pos[1]] != 1:  # 不会撞墙
                            kill_path += d
                            kill_path += counter_act_map[d]
                    kill_path = kill_path[:-1]  # 最后一步不用再回来
                kill_path = kill_path[:my_speed]

                # 杀完剩下一两个单位长度，那也别杀了
                if my_len - len(kill_path) < 3:
                    kill_path = ''

        def get_dir_mask(next_pos, consider_body_head=True):
            if not 0 <= next_pos[0] < map_len or not 0 <= next_pos[1] < map_wid:  # go out of map
                return 0
            if ban_wall_walk:
                if img[CH_WALL][next_pos[0], next_pos[1]] == 1:  # collide with wall
                    if my_prop_power > 2:
                        return 0
            if consider_body_head:  # mask得并不完全，结算的时候吃星星尾巴会变长
                if len(self._my_heads_pos) > 0:
                    if img[CH_MY_HEADS_POS][next_pos[0], next_pos[1]] > 0:  # collide with previous heads
                        return 0
            return 1

        # get action masks
        mask = np.ones((6,))
        after_up_pos = self._my_front_pos + [0, 1]
        after_left_pos = self._my_front_pos + [-1, 0]
        after_down_pos = self._my_front_pos + [0, -1]
        after_right_pos = self._my_front_pos + [1, 0]
        mask[0] = get_dir_mask(next_pos=after_up_pos)  # for w
        mask[1] = get_dir_mask(next_pos=after_left_pos)  # for a
        mask[2] = get_dir_mask(next_pos=after_down_pos)  # for s
        mask[3] = get_dir_mask(next_pos=after_right_pos)  # for d
        if len(self._round_action) == 0:
            mask[4] = 0  # for stop
        if len(self._round_action) > 0 or not (self._in_round_save_len == 0 and 3 <= my_len <= my_speed + 1):
            mask[5] = 0  # for high-level jump back
        if sum(mask) == 0:  # 走到死路，允许撞自己
            mask[0] = get_dir_mask(next_pos=after_up_pos, consider_body_head=False)
            mask[1] = get_dir_mask(next_pos=after_left_pos, consider_body_head=False)
            mask[2] = get_dir_mask(next_pos=after_down_pos, consider_body_head=False)
            mask[3] = get_dir_mask(next_pos=after_right_pos, consider_body_head=False)
            if sum(mask) == 0:  # 真要是还没得走，那就随便走一步撞吧
                mask[np.random.randint(4)] = 1

        feature = {'img_input': img, 'mlp_input': mlp_input, 'mask': mask}
        return feature, kill_path

    def convert_action(self, action: int):
        mapping = {0: 'w', 1: 'a', 2: 's', 3: 'd', 4: 'stop', 5: 'reverse'}
        action = mapping[action]
        self._last_micro_action = action
        if action in ['w', 'a', 's', 'd']:
            self._inner_steps_left -= 1
            self._round_action += action
        else:
            if action == 'stop':
                assert len(self._round_action) > 0
            if action == 'reverse':
                my_player_idx = self.obs['tableinfo']['players'].index(self.player_name)
                my_snake_pos = self.obs['gameinfo']['Map']['SnakePosition'][my_player_idx]
                for p1, p2 in zip(my_snake_pos[:-1], my_snake_pos[1:]):
                    diff = [p2[0]-p1[0], p2[1]-p1[1]]
                    idx = [[0, 1], [-1, 0], [0, -1], [1, 0]].index(diff)
                    self._inner_steps_left -= 1
                    self._round_action += mapping[idx]

        if action == 'stop' or self._inner_steps_left == 0:
            return_action = self._round_action
            self._round_action = ''
            return return_action
        else:
            return None


def onehot(num_feat, idx):
    arr = np.zeros(num_feat)
    arr[idx] = 1
    return arr


def multihot(num_feat, idx):
    arr = np.zeros(num_feat)
    arr[:idx] = 1
    return arr


def preprocess_obs(o):
    o = copy.deepcopy(o)
    if int(o['gameinfo']['Map']['Time']) == 0:  # first obs
        o['gameinfo']['Map']['Score'] = [3.5] * 6
        for i in range(N_SNAKE):
            o['gameinfo']['Player'][i]['Score'] = 3.5

    all_score_len = sorted([o['gameinfo']['Player'][i]['Score_len'] for i in range(N_SNAKE)])
    all_score_kill = sorted([o['gameinfo']['Player'][i]['Score_kill'] for i in range(N_SNAKE)])
    all_score_time = sorted([o['gameinfo']['Player'][i]['Score_time'] for i in range(N_SNAKE)])

    def calc_rank_score(name, score_list):
        if type(o['gameinfo']['Player'][i][name]) == int:
            o['gameinfo']['Player'][i][f'{name}_origin'] = o['gameinfo']['Player'][i][name]
            score_min = score_list.index(o['gameinfo']['Player'][i][name]) + 1
            score_max = 6 - list(reversed(score_list)).index(o['gameinfo']['Player'][i][name])
            o['gameinfo']['Player'][i][name] = (score_min + score_max) / 2.

    for i in range(N_SNAKE):
        if o['gameinfo']['Player'][i]['Act'] == '':
            o['gameinfo']['Player'][i]['Act'] = None
        if type(o['gameinfo']['Player'][i]['DelAct']) == bool:
            o['gameinfo']['Player'][i]['DelAct'] = int(o['gameinfo']['Player'][i]['DelAct'])
        calc_rank_score('Score_len', all_score_len)
        calc_rank_score('Score_kill', all_score_kill)
        calc_rank_score('Score_time', all_score_time)
        assert (o['gameinfo']['Player'][i]['Score_len'] +
                o['gameinfo']['Player'][i]['Score_time'] +
                o['gameinfo']['Player'][i]['Score_kill'] * 1.5) / 3.5 \
               == o['gameinfo']['Player'][i]['Score']

    return o


def one_snake_suicide(game_info, player_idx):
    """找最近的墙自杀"""
    game_info = copy.deepcopy(game_info)
    my_info = game_info['Player'][player_idx]
    n_alive_player = sum([not game_info['Player'][i]['IsDead'] for i in range(N_SNAKE)])
    if not my_info['IsDead'] and n_alive_player == 1:
        others_score_len = [game_info['Player'][i]['Score_len_origin'] for i in range(N_SNAKE) if i != player_idx]
        my_potential_len = min(my_info['SaveLength'], my_info['Speed']) + my_info['Score_len_origin']
        if my_potential_len > max(others_score_len):
            wall_pos = game_info['Map']['WallPosition']
            front_pos = game_info['Map']['SnakePosition'][player_idx][0]
            nearest_wall = None
            nearest_dist = 99999
            for wp in wall_pos:
                to_wall_dist = abs(wp[0] - front_pos[0]) + abs(wp[1] - front_pos[1])
                if to_wall_dist < nearest_dist:
                    nearest_dist = to_wall_dist
                    nearest_wall = wp
            if nearest_dist <= my_info['Speed']:
                action = ''  # 'w' * my_info['Speed']
                x_diff, y_diff = nearest_wall[0] - front_pos[0], nearest_wall[1] - front_pos[1]
                if x_diff > 0:
                    action += 'd' * x_diff
                else:
                    action += 'a' * abs(x_diff)
                if y_diff > 0:
                    action += 'w' * y_diff
                else:
                    action += 's' * abs(y_diff)
                steps_left = my_info['Speed'] - abs(x_diff) - abs(y_diff)
                front_pos = copy.deepcopy(np.array(nearest_wall))
                mapping = {'w': np.array([0, 1]), 'a': np.array([-1, 0]),
                           's': np.array([0, -1]), 'd': np.array([1, 0])}
                while steps_left > 0:
                    act = np.random.choice(['w', 'a', 's', 'd'])
                    after_act_pos = front_pos + mapping[act]
                    if 0 <= after_act_pos[0] < 55 and 0 <= after_act_pos[1] < 40:
                        action += act
                        front_pos = after_act_pos
                        steps_left -= 1
                return action


class FinalAI:
    def __init__(self, player_name):
        self._player_name = player_name

        self.agent = ...  # our agent part is not open-sourced
        self.init = False

        self.converter = Converter()

    def get_action(self, player_idx, game_info, table_info):
        if (
            (game_info["Player"][player_idx]["IsDead"])
            or (game_info["Player"][player_idx]["NowDead"])
            or (len(game_info["Map"]["SnakePosition"][player_idx]) == 0)
        ):
            return np.random.choice(['w', 'a', 's', 'd'])  # 挂了，随便返回个动作

        obs = {'gameinfo': game_info, 'tableinfo': table_info}

        if int(game_info['Map']['Time']) == 0 or (not self.init):
            self.converter.reset(init_obs=obs, player_name=self._player_name)

        action = None
        while action is None:
            state, kill_path = self.converter.convert_state(obs)
            if kill_path != '':
                action = kill_path
                break
            micro_act = self.agent(state)
            action = self.converter.convert_action(micro_act)

        suicide_action = one_snake_suicide(preprocess_obs(obs)['gameinfo'], player_idx)
        if suicide_action is not None:
            return suicide_action
        else:
            return action
