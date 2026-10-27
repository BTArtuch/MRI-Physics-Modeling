"""Generate and render a spin-echo pulse-sequence animation."""

import argparse
import os
import sys

import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from src.spin_echo.animate import render_animation
from src.spin_echo.simulate import generate_se_trajectory


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--t1", type=float, default=1.0)
    parser.add_argument("--t2", type=float, default=0.6)
    parser.add_argument("--te", type=float, default=0.8)
    parser.add_argument("--dt", type=float, default=0.002)
    parser.add_argument("--t-90", type=float, default=0.1)
    parser.add_argument("--t-180", type=float, default=0.1)
    parser.add_argument(
        "--output-dir",
        default=os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "output", "videos")),
        help="Directory for the rendered GIF.",
    )
    args = parser.parse_args()

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    export_path = os.path.join(project_root, "data", "exports", "spin_echo_simulation.csv")
    output_path = os.path.join(args.output_dir, "SpinEcho.gif")

    trajectory = generate_se_trajectory(
        t1=args.t1,
        t2=args.t2,
        te=args.te,
        dt=args.dt,
        t_90=args.t_90,
        t_180=args.t_180,
    )
    os.makedirs(os.path.dirname(export_path), exist_ok=True)
    trajectory.to_csv(export_path, index=False)
    print(f"Trajectory saved to {export_path}")
    render_animation(
        export_path,
        output_path,
        t_90=args.t_90,
        te=args.te,
        t_180=args.t_180,
    )


if __name__ == "__main__":
    main()
