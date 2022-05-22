import pickle
import time

from snake_env.visualizer.visualizer import SnakeEnvVisualizer


def test_data_replay():
    with open("assets/sample_data.pkl", "rb") as f:
        data = pickle.load(f)
    visualizer = SnakeEnvVisualizer()
    for state in data:
        visualizer.render(state)
        time.sleep(0.5)


def test_save_video(tmp_path):
    with open("assets/sample_data.pkl", "rb") as f:
        data = pickle.load(f)
    visualizer = SnakeEnvVisualizer(save_video=True, video_dir=tmp_path)
    for state in data:
        visualizer.render(state)
    visualizer.dump_video()
