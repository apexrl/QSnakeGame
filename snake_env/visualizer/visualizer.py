from typing import Tuple
import os
import pygame
import logging
import numpy as np
from scipy import stats

try:
    import cv2
except ImportError:
    pass

IMAGES_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "assets/images"
)
# FONTS_DIR = os.path.join(
#     os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "assets/fonts"
# )

ACT_TO_DIRECTION = {
    "w": 0,
    "d": 1,
    "s": 2,
    "a": 3,
}

PLAYER_COLORS = [
    (162, 155, 254),
    (0, 168, 255),
    (25, 154, 150),
    (253, 210, 48),
    (250, 116, 115),
    (240, 103, 221),
]

def get_font_name():
    flist = pygame.font.get_fonts()
    f = flist[0]
    for fname in flist:
        if "hei" in fname:
            f = fname
            break
    
    fname = pygame.font.match_font(fname)

    return fname
    

class SnakeEnvVisualizer:
    def __init__(
        self,
        player_num: int = 6,
        map_size: Tuple[int, int] = [55, 40],
        block_pix: int = 40,
        margin_pix: int = 10,
        save_video: bool = False,
        video_dir: str = None,
    ):
        self.pygame_inited = False
        self.map_size = np.array(map_size)
        self.player_num = player_num

        if save_video:
            assert video_dir is not None
            os.makedirs(video_dir, exist_ok=True)
        self.save_video = save_video
        self.video_dir = video_dir
        self.video_frames = []

        self.block_pix = block_pix
        self.margin_pix = margin_pix
        self.info_pix = np.array([block_pix * 15, 0])  # other text info displayed at right
        self.main_pix = np.array(self.map_size * block_pix) + 2 * margin_pix  # main game window
        self.screen_pix = self.main_pix + self.info_pix

    def _init_pygame(self):
        pygame.init()
        try:
            self.screen = pygame.display.set_mode(self.screen_pix)
        except pygame.error:
            logging.warning(" No display available, falling back to no window mode")
            os.environ["SDL_VIDEODRIVER"] = "dummy"
            self.screen = pygame.display.set_mode(self.screen_pix)
        pygame.display.set_caption('Snake Env')

        # use any font
        fname = get_font_name()
        # print("[Warning] use a random font in system, you can modify the")
        self.time_font = pygame.font.Font(fname, int(self.block_pix * 3 / 2))
        self.name_font = pygame.font.Font(fname, self.block_pix)
        self.info_font = pygame.font.Font(fname, int(self.block_pix * 2 / 3))
        self.elements = [
            "empty",
            "wall",
            "sugar",
            "strong",
            "double",
            "speed",
            *[f"snake_body_{i}" for i in range(self.player_num)],
            *[f"snake_head_{i}" for i in range(self.player_num)],
        ]
        self._load_images()
        self._clear_screen()
        self._update_screen()
        self.pygame_inited = True

    def _load_images(self):
        self.element_images = {}
        for name in self.elements:
            self.element_images[name] = pygame.transform.scale(
                pygame.image.load(os.path.join(IMAGES_DIR, f"{name}.png")),
                (self.block_pix, self.block_pix),
            )

    def _update_screen(self):
        pygame.display.flip()

    def _clear_screen(self):
        self.screen.fill((240, 242, 245))
        for x in range(self.map_size[0]):
            for y in range(self.map_size[1]):
                self.screen.blit(
                    self.element_images["empty"],
                    (
                        x * self.block_pix + self.margin_pix,
                        y * self.block_pix + self.margin_pix,
                    ),
                )

    def _update_elements(self, positions, name: str, rotation=0):
        if rotation == 0:
            image = self.element_images[name]
        else:
            image = pygame.transform.rotate(self.element_images[name], rotation)
        for x, y in positions:
            self.screen.blit(
                image,
                (
                    x * self.block_pix + self.margin_pix,
                    y * self.block_pix + self.margin_pix,
                ),
            )

    def _get_head_direction(self, last_act, snake_positions):
        # UP: 0, RIGHT: 1, DOWN: 2, LEFT: 3
        if last_act is None:
            delta_pos = np.array(snake_positions[0]) - np.array(snake_positions[1])
            if delta_pos[0] == 0:
                if delta_pos[1] > 0:
                    return 0
                else:
                    return 2
            elif delta_pos[1] == 0:
                if delta_pos[0] > 0:
                    return 1
                else:
                    return 3
        return ACT_TO_DIRECTION[last_act]

    def _get_adjusted_positions(self, positions):
        for idx in range(len(positions)):
            positions[idx][1] = self.map_size[1] - positions[idx][1] - 1
        return positions

    def dump_video(self, save_path: str = None):
        assert self.save_video is True
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        if save_path is None:
            save_path = os.path.join(self.video_dir, "output.mp4"),
        out = cv2.VideoWriter(
            save_path,
            fourcc,
            1.0,
            self.screen_pix,
        )
        for frame in self.video_frames:
            out.write(
                cv2.cvtColor(frame.transpose((1, 0, 2)), cv2.COLOR_BGR2RGB)
            )
        out.release()
        cv2.destroyAllWindows()

    def render(self, game_info):
        if not self.pygame_inited:
            self._init_pygame()

        self._clear_screen()
        map_info = game_info["gameinfo"]["Map"]
        player_info = game_info["gameinfo"]["Player"]
        last_act = player_info[0]["LastAct"]

        sugar_positions = map_info["SugarPosition"]
        sugar_positions = self._get_adjusted_positions(sugar_positions)
        self._update_elements(sugar_positions, "sugar")

        # speed
        speed_positions = map_info["PropPosition"][0]
        speed_positions = self._get_adjusted_positions(speed_positions)
        self._update_elements(speed_positions, "speed")

        # strong
        strong_positions = map_info["PropPosition"][1]
        strong_positions = self._get_adjusted_positions(strong_positions)
        self._update_elements(strong_positions, "strong")

        # double
        double_positions = map_info["PropPosition"][2]
        double_positions = self._get_adjusted_positions(double_positions)
        self._update_elements(double_positions, "double")

        # snakes
        for p_id in range(self.player_num):
            snake_positions = map_info["SnakePosition"][p_id]
            if len(snake_positions) == 0:
                continue
            last_act = player_info[p_id]["LastAct"]
            rotation = self._get_head_direction(last_act, snake_positions)
            snake_positions = self._get_adjusted_positions(snake_positions)
            head_position = snake_positions[0]
            body_positions = snake_positions[1:]
            self._update_elements(
                [head_position], f"snake_head_{p_id}", rotation=-rotation * 90
            )
            self._update_elements(body_positions, f"snake_body_{p_id}")

        # wall
        wall_positions = map_info["WallPosition"]
        wall_positions = self._get_adjusted_positions(wall_positions)
        self._update_elements(wall_positions, "wall")

        self._render_text_info(game_info)

        self._update_screen()

        if self.save_video:
            self.video_frames.append(pygame.surfarray.array3d(self.screen))

    def _render_text_info(self, game_info):
        time_text = "Time: {}".format(game_info["gameinfo"]["Map"]["Time"])
        time_pix = self.block_pix * 2
        self.screen.blit(
            self.name_font.render(time_text, True, (255, 0, 0)),
            (
                self.main_pix[0] + self.margin_pix,
                0,
            ),
        )

        player_info = game_info["gameinfo"]["Player"]
        # By default, stats.rankdata is ascending order, so here we take negative score
        # to reverse it.
        ranks = stats.rankdata([-p["Score"] for p in player_info], method="min")
        for p_id in range(self.player_num):
            player_info_text = f"{player_info[p_id]['Name']}:"
            self.screen.blit(
                self.name_font.render(player_info_text, True, PLAYER_COLORS[p_id]),
                (
                    self.main_pix[0] + self.margin_pix,
                    p_id * (self.block_pix * 6) + time_pix,
                ),
            )

            first_line_text = "Score: {:7}  Rank: {:2}  Kill: {:2}".format(
                round(player_info[p_id]['Score'], 4),
                ranks[p_id],
                player_info[p_id]["Score_kill"],
            )
            self.screen.blit(
                self.info_font.render(first_line_text, True, (0, 0, 0)),
                (
                    self.main_pix[0] + self.margin_pix,
                    p_id * (self.block_pix * 6) + 2 * self.block_pix + time_pix,
                ),
            )

            second_line_text = "Speed: {:3}  Length: {:3}  Time: {:3}".format(
                player_info[p_id]["Speed"],
                player_info[p_id]["Score_len"],
                player_info[p_id]["Score_time"],
            )
            self.screen.blit(
                self.info_font.render(second_line_text, True, (0, 0, 0)),
                (
                    self.main_pix[0] + self.margin_pix,
                    p_id * (self.block_pix * 6) + 3 * self.block_pix + time_pix,
                ),
            )

            third_line_text = "PropSpeed: {:3}  PropShield: {:3}  PropDouble: {:3}".format(
                player_info[p_id]["Prop"]["speed"],
                player_info[p_id]["Prop"]["strong"],
                player_info[p_id]["Prop"]["double"],
            )
            self.screen.blit(
                self.info_font.render(third_line_text, True, (0, 0, 0)),
                (
                    self.main_pix[0] + self.margin_pix,
                    p_id * (self.block_pix * 6) + 4 * self.block_pix + time_pix,
                ),
            )
