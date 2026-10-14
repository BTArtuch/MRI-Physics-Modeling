# src/fid/simulate.py
import numpy as np
import pandas as pd

def generate_fid_trajectory(export_path, t1=1.0, t2=0.4, dt=0.002, total_time=2.5):
    time = np.arange(0, total_time, dt)
    
    freq = 2.0 
    omega0 = 2 * np.pi * freq
    
    # T1 Recovery: Vectors stand back up along the Z-axis
    mz = 1.0 * (1 - np.exp(-time / t1))
    
    # T2 Decay: Vectors shrink in the transverse plane
    mxy_magnitude = 1.0 * np.exp(-time / t2)
    
    # 4 phases offset by 90 degrees
    phases = [0, np.pi/2, np.pi, 3*np.pi/2]
    
    data = {'Time': time, 'Mz': mz}
    for i, phase in enumerate(phases):
        # Calculate Laboratory frame coordinates for each phase
        data[f'Mx_{i}'] = mxy_magnitude * np.cos(omega0 * time + phase)
        data[f'My_{i}'] = mxy_magnitude * np.sin(omega0 * time + phase)
        
    df = pd.DataFrame(data)
    df.to_csv(export_path, index=False)
    
    print(f"Simulation complete. FID trajectory saved to {export_path}")
    return export_path