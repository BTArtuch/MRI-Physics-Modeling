# src/relaxation/animate.py
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import os

def render_video(csv_path, output_path):
    df = pd.read_csv(csv_path)
    
    skip_frames = max(len(df) // 200, 1) 
    df = df.iloc[::skip_frames].reset_index(drop=True)

    # Make the figure taller to fit 4 plots (2x2 grid)
    fig = plt.figure(figsize=(14, 10))
    fig.suptitle('MRI Relaxation Dynamics', fontsize=18)
    
    # --- TOP ROW: 3D PLOTS ---
    ax1 = fig.add_subplot(221, projection='3d')
    ax1.set_title('Laboratory Frame (3D)')
    
    ax2 = fig.add_subplot(222, projection='3d')
    ax2.set_title('Rotating Frame (3D)')
    
    for ax in [ax1, ax2]:
        ax.set_xlim([-1.2, 1.2])
        ax.set_ylim([-1.2, 1.2])
        ax.set_zlim([0, 1.2])
        ax.set_xlabel('Mx')
        ax.set_ylabel('My')
        ax.set_zlabel('Mz')
        ax.view_init(elev=20, azim=45)

    # --- BOTTOM ROW: 2D PLOTS ---
    ax3 = fig.add_subplot(223)
    ax3.set_title('Transverse Decay (T2)')
    ax3.set_xlim([0, df['Time'].max()])
    ax3.set_ylim([0, 1.1])
    ax3.set_xlabel('Time (s)')
    ax3.set_ylabel('Mxy Magnitude')
    ax3.grid(True)

    ax4 = fig.add_subplot(224)
    ax4.set_title('Longitudinal Recovery (T1)')
    ax4.set_xlim([0, df['Time'].max()])
    ax4.set_ylim([0, 1.1])
    ax4.set_xlabel('Time (s)')
    ax4.set_ylabel('Mz Magnitude')
    ax4.grid(True)

    # Initialize 3D lines
    line_lab, = ax1.plot([], [], [], lw=2, color='blue', alpha=0.5)
    line_rot, = ax2.plot([], [], [], lw=2, color='green', alpha=0.5)
    
    # Initialize 2D lines and moving dots
    line_mxy, = ax3.plot([], [], lw=2, color='purple')
    dot_mxy, = ax3.plot([], [], 'ro')  # 'ro' = red circle
    
    line_mz, = ax4.plot([], [], lw=2, color='orange')
    dot_mz, = ax4.plot([], [], 'ro')

    def update(frame):
        # Clear previous 3D arrows
        for ax in [ax1, ax2]:
            while ax.collections:
                ax.collections[0].remove()
        
        # Get current frame data
        t = df['Time'].iloc[frame]
        mz = df['Mz'].iloc[frame]
        mxy = df['Mxy'].iloc[frame]
        mx_lab, my_lab = df['Mx_lab'].iloc[frame], df['My_lab'].iloc[frame]
        mx_rot, my_rot = df['Mx_rot'].iloc[frame], df['My_rot'].iloc[frame]
        
        # 1. Update 3D Arrows
        ax1.quiver(0, 0, 0, mx_lab, my_lab, mz, color='red', length=1.0, arrow_length_ratio=0.1)
        ax2.quiver(0, 0, 0, mx_rot, my_rot, mz, color='red', length=1.0, arrow_length_ratio=0.1)
        
        # 2. Update 3D Trails
        line_lab.set_data(df['Mx_lab'].iloc[:frame], df['My_lab'].iloc[:frame])
        line_lab.set_3d_properties(df['Mz'].iloc[:frame])
        
        line_rot.set_data(df['Mx_rot'].iloc[:frame], df['My_rot'].iloc[:frame])
        line_rot.set_3d_properties(df['Mz'].iloc[:frame])
        
        # 3. Update 2D Trails and Moving Dots
        line_mxy.set_data(df['Time'].iloc[:frame], df['Mxy'].iloc[:frame])
        dot_mxy.set_data([t], [mxy])  # Wrap in lists to plot a single point
        
        line_mz.set_data(df['Time'].iloc[:frame], df['Mz'].iloc[:frame])
        dot_mz.set_data([t], [mz])
        
        return line_lab, line_rot, line_mxy, dot_mxy, line_mz, dot_mz

    # Generate animation
    ani = animation.FuncAnimation(fig, update, frames=len(df), interval=50, blit=False)
    
    # Export 
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    try:
        ani.save(output_path, fps=20)
        print(f"Success: Video saved to {output_path}")
    except Exception as e:
        print("FFmpeg not found on system. Falling back to GIF...")
        fallback_path = output_path.replace('.mp4', '.gif')
        ani.save(fallback_path, writer='pillow', fps=20)
        print(f"Success: GIF saved to {fallback_path}")