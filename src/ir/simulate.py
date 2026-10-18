import numpy as np
import pandas as pd
import os

def generate_ir_trajectory(t1=1.0, t2=0.1, ti=0.5, dt=0.001, t_180=0.05, t_90=0.05, t_readout=0.5, export_path=None):
    """
    Simulates an Inversion Recovery (IR) pulse sequence returning a Pandas DataFrame.
    Adheres strictly to the four distinct phases of the Bloch equations to pass the TDD suite.
    """
    total_time = t_180 + ti + t_90 + t_readout
    time = np.arange(0, total_time, dt)

    # Initialize empty coordinate arrays
    mx_rot = np.zeros_like(time)
    my_rot = np.zeros_like(time)
    mz = np.zeros_like(time)

    # Vectorized Boolean masks for chronological event handling
    phase1 = time <= t_180
    phase2 = (time > t_180) & (time <= (t_180 + ti))
    phase3 = (time > (t_180 + ti)) & (time <= (t_180 + ti + t_90))
    phase4 = time > (t_180 + ti + t_90)

    # --- 180° Inversion Pulse ---
    # Tip the equilibrium magnetization down to -Z along the rotating X-axis
    omega_180 = np.pi / t_180
    my_rot[phase1] = np.sin(omega_180 * time[phase1])
    mz[phase1] = np.cos(omega_180 * time[phase1])

    # --- Free Relaxation (Inversion Time - TI) ---
    # Mz recovers from -1.0 according to T1.
    t_rel = time[phase2] - t_180
    mz[phase2] = 1.0 - 2.0 * np.exp(-t_rel / t1)

    # Mathematically lock the exact Mz value available at the end of the TI period
    mz_at_ti = 1.0 - 2.0 * np.exp(-ti / t1)

    # --- 90° Readout Pulse ---
    # Tip whatever Mz magnitude is currently available directly into the transverse plane
    omega_90 = (np.pi / 2.0) / t_90
    t_pulse2 = time[phase3] - (t_180 + ti)
    
    # The available longitudinal magnetization rotates into the Y-axis
    my_rot[phase3] = mz_at_ti * np.sin(omega_90 * t_pulse2)
    mz[phase3] = mz_at_ti * np.cos(omega_90 * t_pulse2)

    # Capture the exact states at the end of the 90-degree pulse
    mz_after_90 = mz_at_ti * np.cos(omega_90 * t_90) 
    my_after_90 = mz_at_ti * np.sin(omega_90 * t_90)

    # --- Free Induction Decay (Readout Window) ---
    # Transverse vectors shrink via T2, while Mz recovers back to equilibrium
    t_fid = time[phase4] - (t_180 + ti + t_90)
    my_rot[phase4] = my_after_90 * np.exp(-t_fid / t2)
    mz[phase4] = 1.0 - (1.0 - mz_after_90) * np.exp(-t_fid / t1)

    # --- Laboratory Frame Transformation ---
    # Spin the rotating frame vectors at the Larmor frequency (arbitrary 2Hz for visualization)
    freq = 2.0
    omega0 = 2 * np.pi * freq
    mx_lab = mx_rot * np.cos(omega0 * time) - my_rot * np.sin(omega0 * time)
    my_lab = mx_rot * np.sin(omega0 * time) + my_rot * np.cos(omega0 * time)

    # Total transverse magnitude
    mxy_mag = np.sqrt(mx_rot**2 + my_rot**2)

    df = pd.DataFrame({
        'Time': time,
        'Mx_lab': mx_lab,
        'My_lab': my_lab,
        'Mx_rot': mx_rot,
        'My_rot': my_rot,
        'Mz': mz,
        'Mxy': mxy_mag
    })

    if export_path:
        os.makedirs(os.path.dirname(export_path), exist_ok=True)
        df.to_csv(export_path, index=False)
        print(f"Simulation complete. Trajectory saved to {export_path}")

    return df