# src/relaxation/animate.py
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import os

def render_video(csv_path, output_path):
    df = pd.read_csv(csv_path)
    
    skip_frames = max(len(df) // 200, 1) 
    df = df.iloc[::skip_frames].reset_index(drop=True)

    fig = plt.figure(figsize=(14, 10))
    fig.suptitle('MRI Dynamics: 90° Excitation & Relaxation', fontsize=18)
    
    gs = fig.add_gridspec(2, 2, height_ratios=[1.4, 1.0], hspace=0.1)
    
    # --- TOP ROW: 3D PLOTS ---
    ax1 = fig.add_subplot(gs[0, 0], projection='3d')
    ax1.set_title('Laboratory Frame (3D)', pad=0)
    
    ax2 = fig.add_subplot(gs[0, 1], projection='3d')
    ax2.set_title('Rotating Frame (3D)', pad=0)
    
    for ax in [ax1, ax2]:
        ax.set_xlim([-1.1, 1.1])
        ax.set_ylim([-1.1, 1.1])
        ax.set_zlim([0, 1.1])
        ax.view_init(elev=20, azim=45)
        ax.set_box_aspect(None, zoom=1.3)
        ax.set_axis_off()
        
        ax.plot([-1.1, 1.1], [0, 0], [0, 0], color='gray', lw=1, linestyle='--')
        ax.plot([0, 0], [-1.1, 1.1], [0, 0], color='gray', lw=1, linestyle='--')
        ax.plot([0, 0], [0, 0], [0, 1.1], color='gray', lw=1, linestyle='--')
        
        ax.text(1.2, 0, 0, 'Mx', color='black', fontsize=10)
        ax.text(0, 1.2, 0, 'My', color='black', fontsize=10)
        ax.text(0, 0, 1.2, 'Mz', color='black', fontsize=10)

    # --- BOTTOM ROW: 2D PLOTS ---
    ax3 = fig.add_subplot(gs[1, 0])
    ax3.set_title('Transverse Plane (Mxy)')
    ax3.set_xlim([0, df['Time'].max()])
    ax3.set_ylim([0, 1.1])
    ax3.set_xlabel('Time (s)')
    ax3.set_ylabel('Mxy Magnitude')
    ax3.grid(True)

    ax4 = fig.add_subplot(gs[1, 1])
    ax4.set_title('Longitudinal Axis (Mz)')
    ax4.set_xlim([0, df['Time'].max()])
    ax4.set_ylim([0, 1.1])
    ax4.set_xlabel('Time (s)')
    ax4.set_ylabel('Mz Magnitude')
    ax4.grid(True)

    # Initialize Trails and Dots
    line_lab, = ax1.plot([], [], [], lw=2, color='blue', alpha=0.5)
    line_rot, = ax2.plot([], [], [], lw=2, color='green', alpha=0.5)
    
    line_mxy, = ax3.plot([], [], lw=2, color='purple')
    dot_mxy, = ax3.plot([], [], 'ro')
    
    line_mz, = ax4.plot([], [], lw=2, color='orange')
    dot_mz, = ax4.plot([], [], 'ro')

    def update(frame):
        for ax in [ax1, ax2]:
            while ax.collections:
                ax.collections[0].remove()
        
        t = df['Time'].iloc[frame]
        mz, mxy = df['Mz'].iloc[frame], df['Mxy'].iloc[frame]
        mx_lab, my_lab = df['Mx_lab'].iloc[frame], df['My_lab'].iloc[frame]
        mx_rot, my_rot = df['Mx_rot'].iloc[frame], df['My_rot'].iloc[frame]
        
        b1x_lab, b1y_lab = df['B1x_lab'].iloc[frame], df['B1y_lab'].iloc[frame]
        b1x_rot = df['B1x_rot'].iloc[frame]
        
        # 1. Draw Magnetization Arrows (Red)
        ax1.quiver(0, 0, 0, mx_lab, my_lab, mz, color='red', length=1.0, arrow_length_ratio=0.1)
        ax2.quiver(0, 0, 0, mx_rot, my_rot, mz, color='red', length=1.0, arrow_length_ratio=0.1)
        
        # 2. Draw B1 RF Pulse Arrows (Orange) if active
        if b1x_rot > 0:
            ax1.quiver(0, 0, 0, b1x_lab, b1y_lab, 0, color='orange', lw=2, length=1.0, arrow_length_ratio=0.1)
            ax2.quiver(0, 0, 0, b1x_rot, 0, 0, color='orange', lw=2, length=1.0, arrow_length_ratio=0.1)
        
        # 3. Update Trails and Dots
        line_lab.set_data(df['Mx_lab'].iloc[:frame], df['My_lab'].iloc[:frame])
        line_lab.set_3d_properties(df['Mz'].iloc[:frame])
        
        line_rot.set_data(df['Mx_rot'].iloc[:frame], df['My_rot'].iloc[:frame])
        line_rot.set_3d_properties(df['Mz'].iloc[:frame])
        
        line_mxy.set_data(df['Time'].iloc[:frame], df['Mxy'].iloc[:frame])
        dot_mxy.set_data([t], [mxy])
        
        line_mz.set_data(df['Time'].iloc[:frame], df['Mz'].iloc[:frame])
        dot_mz.set_data([t], [mz])
        
        return line_lab, line_rot, line_mxy, dot_mxy, line_mz, dot_mz

    ani = animation.FuncAnimation(fig, update, frames=len(df), interval=50, blit=False)
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    try:
        ani.save(output_path, fps=20)
        print(f"Success: Video saved to {output_path}")
    except Exception as e:
        print("FFmpeg not found on system. Falling back to GIF...")
        fallback_path = output_path.replace('.mp4', '.gif')
        ani.save(fallback_path, writer='pillow', fps=20)
        print(f"Success: GIF saved to {fallback_path}")