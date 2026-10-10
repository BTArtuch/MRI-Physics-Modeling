# src/relaxation/run.py
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.relaxation.simulate import generate_trajectory
from src.relaxation.animate import render_video

if __name__ == "__main__":
    export_path = "data/exports/standalone_relaxation.csv"
    output_video = "output/videos/T1T2Relaxation.mp4"
    
    os.makedirs(os.path.dirname(export_path), exist_ok=True)
    
    print("1. Calculating Bloch equations via NumPy...")
    
    # ---------------------------------------------------------
    # t_pulse: 0.5s excitation phase
    # total_time: Extended to 2.5s to capture the full curve
    # ---------------------------------------------------------
    generate_trajectory(export_path, t1=1.5, t2=0.8, dt=0.001, total_time=4.0, t_pulse=0.25)
    
    print("2. Rendering 3D Matplotlib animation...")
    render_video(export_path, output_video)
    