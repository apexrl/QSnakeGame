from typing import List
import random
import numpy as np

from snake_env_cpp import SnakeGame
from snake_env.utils import int_to_vec
from snake_env.visualizer import SnakeEnvVisualizer


class SnakeEnv:
    def __init__(
        self,
        player_num: int = 6,
        player_ids: List[str] = None,
        table_id: int = 0,
        visualize: bool = False,
    ):
        self._player_num = player_num
        self._game = SnakeGame(player_num)
        self._table_id = table_id
        if visualize:
            self.visualizer = SnakeEnvVisualizer(player_num)
        else:
            self.visualizer = None
        if player_ids is None:
            self._player_ids = [
                "Ubiq134",
                *[
                    "Ubiq%03d" % num
                    for num in random.sample(
                        set(range(1000)) - set([134]), player_num - 1
                    )
                ],
            ]
        else:
            assert len(player_ids) == player_num
            self._player_ids = player_ids

    @property
    def player_ids(self):
        return self._player_ids

    @property
    def table_id(self):
        return self._table_id

    @property
    def player_num(self):
        return self._player_num

    def reset(self):
        self._game.reset()
        return self._get_game_info()

    def step(self, actions):
        self._game.step(actions)
        return self._get_game_info(), 0, self._game.is_game_over(), {}

    def render(self):
        if self.visualizer is None:
            raise AttributeError(
                "Env is not configurated with a visualizer. Please recreate with visualize=True"
            )
        self.visualizer.render(self._get_game_info())

    def _get_game_info(self):
        game_info = {k: {} for k in ["gameinfo", "tableinfo"]}
        string_infos = self._game.get_snake_string_infos()
        int_infos = self._game.get_snake_int_infos()
        double_infos = self._game.get_snake_double_infos()
        map_info = self._game.get_map_info()
        map_position = self._game.get_map_position()

        # Collect map information
        game_info["gameinfo"]["Map"] = {}
        game_info["gameinfo"]["Map"]["Length"] = map_info["Length"]
        game_info["gameinfo"]["Map"]["Width"] = map_info["Width"]
        game_info["gameinfo"]["Map"]["Score"] = [
            double_infos[p_id]["Score"] for p_id in range(self.player_num)
        ]
        # np.array().tolist() is used to transform all tuples to lists.
        game_info["gameinfo"]["Map"]["SnakePosition"] = [
            np.array(positions).tolist()
            for positions in map_position[: self.player_num]
        ]
        game_info["gameinfo"]["Map"]["SugarPosition"] = np.array(
            map_position[self.player_num]
        ).tolist()
        game_info["gameinfo"]["Map"]["WallPosition"] = np.array(
            map_position[self.player_num + 1]
        ).tolist()
        game_info["gameinfo"]["Map"]["PropPosition"] = [
            np.array(positions).tolist()
            for positions in map_position[self.player_num + 2 :]
        ]
        game_info["gameinfo"]["Map"]["Time"] = map_info["Time"]

        # Collect player information
        game_info["gameinfo"]["Player"] = []
        for p_id in range(self.player_num):
            player_info = {}
            player_info["Name"] = self.player_ids[p_id]
            player_info["Num"] = int_infos[p_id]["Num"]
            # To be aligned with the result returned from web.
            if string_infos[p_id]["LastAct"] == "":
                player_info["LastAct"] = None
            else:
                player_info["LastAct"] = string_infos[p_id]["LastAct"]
            if string_infos[p_id]["Act"] == "":
                player_info["Act"] = None
            else:
                player_info["Act"] = string_infos[p_id]["Act"]
            player_info["IsDead"] = bool(int_infos[p_id]["IsDead"])
            player_info["NowDead"] = bool(int_infos[p_id]["NowDead"])
            player_info["Speed"] = int_infos[p_id]["Speed"]
            player_info["Kill"] = int_infos[p_id]["Kill"]
            player_info["KillList"] = int_to_vec(int_infos[p_id]["KillList"])
            player_info["KilledList"] = int_to_vec(int_infos[p_id]["KilledList"])
            player_info["SaveLength"] = int_infos[p_id]["SaveLength"]

            player_info["Prop"] = {}
            player_info["Prop"]["speed"] = int_infos[p_id]["Prop_speed"]
            player_info["Prop"]["strong"] = int_infos[p_id]["Prop_strong"]
            player_info["Prop"]["double"] = int_infos[p_id]["Prop_double"]

            player_info["DelAct"] = int_infos[p_id]["DelAct"]
            player_info["Score_len"] = int_infos[p_id]["Score_len"]
            player_info["Score_kill"] = int_infos[p_id]["Score_kill"]
            player_info["Score_time"] = int_infos[p_id]["Score_time"]
            player_info["Score"] = double_infos[p_id]["Score"]
            game_info["gameinfo"]["Player"].append(player_info)

        # Collect table information
        game_info["tableinfo"]["table_num"] = self.table_id
        game_info["tableinfo"]["players"] = self.player_ids

        return game_info
