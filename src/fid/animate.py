# src/fid/animate.py
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import os

def render_fid_video(csv_path, output_path):
    df = pd.read_csv(csv_path)
    
    skip_frames = max(len(df) // 200, 1) 
    df = df.iloc[::skip_frames].reset_index(drop=True)

    fig = plt.figure(figsize=(14, 6))
    fig.suptitle('Free Induction Decay (FID): Return to Equilibrium', fontsize=18)
    
    gs = fig.add_gridspec(1, 2, width_ratios=[1.0, 1.2], wspace=0.2)
    
    # --- LEFT: 3D LABORATORY FRAME ---
    ax1 = fig.add_subplot(gs[0], projection='3d')
    ax1.set_title('Laboratory Frame (3D Spiraling)')
    
    # Expanded boundaries to accommodate longer vectors
    ax1.set_xlim([-1.3, 1.3])
    ax1.set_ylim([-1.3, 1.3])
    ax1.set_zlim([0, 1.3]) 
    ax1.view_init(elev=20, azim=45)
    ax1.set_box_aspect(None, zoom=1.3)
    ax1.set_axis_off()
    
    # Expanded custom XYZ axes
    ax1.plot([-1.3, 1.3], [0, 0], [0, 0], color='gray', lw=1, linestyle='--')
    ax1.plot([0, 0], [-1.3, 1.3], [0, 0], color='gray', lw=1, linestyle='--')
    ax1.plot([0, 0], [0, 0], [0, 1.3], color='gray', lw=1, linestyle='--')
    
    # Pushed labels slightly further out
    ax1.text(1.4, 0, 0, 'Mx', color='black', fontsize=10)
    ax1.text(0, 1.4, 0, 'My', color='black', fontsize=10)
    ax1.text(0, 0, 1.4, 'Mz', color='black', fontsize=10)

    # --- RIGHT: 2D FID SIGNAL PLOT ---
    ax2 = fig.add_subplot(gs[1])
    ax2.set_title('Damped Oscillatory Signal (Transverse Decay)')
    ax2.set_xlim([0, df['Time'].max()])
    ax2.set_ylim([-1.1, 1.1])
    ax2.set_xlabel('Time (s)')
    ax2.set_ylabel('Amplitude (Mx Projection)')
    ax2.grid(True)

    colors = ['red', 'green', 'blue', 'black']
    
    lines_fid = []
    dots_fid = []
    for i in range(4):
        line, = ax2.plot([], [], lw=2, color=colors[i], alpha=0.8)
        dot, = ax2.plot([], [], 'o', color=colors[i])
        lines_fid.append(line)
        dots_fid.append(dot)

    def update(frame):
        while ax1.collections:
            ax1.collections[0].remove()
        
        t = df['Time'].iloc[frame]
        mz = df['Mz'].iloc[frame]
        
        for i in range(4):
            mx = df[f'Mx_{i}'].iloc[frame]
            my = df[f'My_{i}'].iloc[frame]
            
            # Increased length parameter to 1.2
            ax1.quiver(0, 0, 0, mx, my, mz, color=colors[i], lw=2, length=1.2, arrow_length_ratio=0.15)
            
            # Trace the 2D FID signal on the right
            lines_fid[i].set_data(df['Time'].iloc[:frame], df[f'Mx_{i}'].iloc[:frame])
            dots_fid[i].set_data([t], [mx])
        
        return lines_fid + dots_fid

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