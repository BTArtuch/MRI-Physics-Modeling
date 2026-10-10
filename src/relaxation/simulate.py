# src/relaxation/simulate.py
import numpy as np
import pandas as pd

def generate_trajectory(export_path, t1=1.0, t2=0.4, dt=0.001, total_time=2.5, t_pulse=0.5):
    time = np.arange(0, total_time, dt)
    
    # Initialize arrays
    mx_rot = np.zeros_like(time)
    my_rot = np.zeros_like(time)
    mz = np.zeros_like(time)
    
    b1x_rot = np.zeros_like(time)
    b1y_rot = np.zeros_like(time)
    
    mx_lab = np.zeros_like(time)
    my_lab = np.zeros_like(time)
    b1x_lab = np.zeros_like(time)
    b1y_lab = np.zeros_like(time)
    
    freq = 2.0 
    omega0 = 2 * np.pi * freq
    
    # Calculate the radial velocity needed to hit 90 degrees (pi/2) over the pulse duration
    omega1 = (np.pi / 2) / t_pulse 
    
    for i, t in enumerate(time):
        # --- PHASE 1: RF Excitation (90-degree pulse) ---
        if t <= t_pulse:
            # B1 field applied along the Rotating X-axis
            b1x_rot[i] = 1.0
            
            # Magnetization tips from Z to Y (Right-hand rule torque)
            mx_rot[i] = 0.0
            my_rot[i] = np.sin(omega1 * t)
            mz[i] = np.cos(omega1 * t)
            
        # --- PHASE 2: Free Relaxation ---
        else:
            t_rel = t - t_pulse
            
            # T1 Recovery and T2 Decay
            mz[i] = 1.0 * (1 - np.exp(-t_rel / t1))
            mxy = 1.0 * np.exp(-t_rel / t2)
            
            mx_rot[i] = 0.0
            my_rot[i] = mxy

        # Transform all vectors into the Laboratory Frame (Precession)
        mx_lab[i] = mx_rot[i] * np.cos(omega0 * t) - my_rot[i] * np.sin(omega0 * t)
        my_lab[i] = mx_rot[i] * np.sin(omega0 * t) + my_rot[i] * np.cos(omega0 * t)
        
        b1x_lab[i] = b1x_rot[i] * np.cos(omega0 * t) - b1y_rot[i] * np.sin(omega0 * t)
        b1y_lab[i] = b1x_rot[i] * np.sin(omega0 * t) + b1y_rot[i] * np.cos(omega0 * t)
        
    mxy_mag = np.sqrt(mx_rot**2 + my_rot**2)
    
    df = pd.DataFrame({
        'Time': time,
        'Mx_lab': mx_lab, 'My_lab': my_lab, 
        'Mx_rot': mx_rot, 'My_rot': my_rot, 
        'Mz': mz, 'Mxy': mxy_mag,
        'B1x_lab': b1x_lab, 'B1y_lab': b1y_lab,
        'B1x_rot': b1x_rot, 'B1y_rot': b1y_rot
    })
    df.to_csv(export_path, index=False)
    
    print(f"Simulation complete. Trajectory saved to {export_path}")
    return export_path