# src/fid/run.py
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.fid.simulate import generate_fid_trajectory
from src.fid.animate import render_fid_video

if __name__ == "__main__":
    export_path = "data/exports/fid_multiphase.csv"
    output_video = "output/videos/FID_Phases.mp4"
    
    os.makedirs(os.path.dirname(export_path), exist_ok=True)
    
    print("1. Calculating Multi-Phase FID equations...")
    generate_fid_trajectory(export_path, t1=1.5, t2=0.6, dt=0.002, total_time=2.5)
    
    print("2. Rendering Side-by-Side Matplotlib animation...")
    render_fid_video(export_path, output_video)