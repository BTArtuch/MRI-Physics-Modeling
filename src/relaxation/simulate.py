# src/relaxation/simulate.py
import numpy as np
import pandas as pd

def generate_trajectory(export_path, t1=1.0, t2=0.1, dt=0.001, total_time=1.0):
    time = np.arange(0, total_time, dt)
    
    # 1. T1 Recovery (Longitudinal)
    mz = 1.0 * (1 - np.exp(-time / t1))
    
    # 2. T2 Decay (Transverse magnitude)
    mxy = 1.0 * np.exp(-time / t2)
    
    # 3. Laboratory Frame (Precession)
    freq = 2.0 
    omega = 2 * np.pi * freq
    mx_lab = mxy * np.cos(omega * time)
    my_lab = mxy * np.sin(omega * time)
    
    # 4. Rotating Frame
    mx_rot = mxy
    my_rot = np.zeros_like(time)
    
    # Save all coordinates AND Time/Mxy to CSV
    df = pd.DataFrame({
        'Time': time,
        'Mx_lab': mx_lab, 'My_lab': my_lab, 
        'Mx_rot': mx_rot, 'My_rot': my_rot, 
        'Mz': mz, 'Mxy': mxy
    })
    df.to_csv(export_path, index=False)
    
    print(f"Simulation complete. Trajectory saved to {export_path}")
    return export_path