import pickle
import argparse

from snake_env.visualizer.visualizer import SnakeEnvVisualizer


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "pkl_path",
        type=str,
        help="Path to the pkl file containing the data to be visualized.",
    )
    parser.add_argument(
        "--save_dir",
        default="./videos",
        type=str,
        help="Directory to save videos",
    )
    args = parser.parse_args()

    with open(args.pkl_path, "rb") as f:
        data = pickle.load(f)
    visualizer = SnakeEnvVisualizer(save_video=True, video_dir=args.save_dir)
    for state in data:
        visualizer.render(state)
    visualizer.dump_video(save_path=args.pkl_path.replace(".pkl", ".mp4"))
