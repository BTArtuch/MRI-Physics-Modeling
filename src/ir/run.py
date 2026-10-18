import os
import sys
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.ir.simulate import generate_ir_trajectory
from src.ir.animate import render_video

if __name__ == "__main__":
    export_path = "data/exports/ir_simulation.csv"
    output_video = "output/videos/InversionRecovery.mp4"
    
    t1_val = 1.0
    ti_null = t1_val * np.log(2)  # Maintain the textbook null point
    
    # 1. Extend pulse durations so the rotation doesn't skip frames
    t_180, t_90 = 0.2, 0.1
    
    # 2. Extend readout time so the vector fully recovers before the GIF loops
    t_readout = 2.0 
    
    print("1. Calculating Vectorized Bloch Equations...")
    generate_ir_trajectory(
        export_path=export_path, 
        t1=t1_val, t2=0.1, ti=ti_null, dt=0.002, 
        t_180=t_180, t_90=t_90, t_readout=t_readout
    )
    
    print("2. Rendering 3-Plot Dashboard...")
    render_video(export_path, output_video, t_180=t_180, ti=ti_null, t_90=t_90)