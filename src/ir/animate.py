import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.patches as patches
import os

def setup_ir_dashboard():
    fig = plt.figure(figsize=(14, 8))
    fig.suptitle('Inversion Recovery (IR) Pulse Sequence', fontsize=18)
    
    gs = fig.add_gridspec(2, 2, width_ratios=[1.2, 1.0], height_ratios=[1, 1], wspace=0.2, hspace=0.3)
    
    # Top Left: Pulse Sequence
    ax_seq = fig.add_subplot(gs[0, 0])
    ax_seq.set_title('Pulse Sequence', pad=10)
    ax_seq.set_axis_off() 
    
    # Bottom Left: Mz Relaxation
    ax_mz = fig.add_subplot(gs[1, 0])
    ax_mz.set_title('$T_1$ Longitudinal Relaxation ($M_0$)')
    ax_mz.set_ylim([-1.1, 1.1])
    ax_mz.set_xlabel('Time (s)')
    ax_mz.set_ylabel('Magnitude')
    ax_mz.grid(True)
    ax_mz.axhline(0, color='black', linewidth=1)
    
    # Right: 3D Rotating Frame (Spans both rows)
    ax_3d = fig.add_subplot(gs[:, 1], projection='3d')
    ax_3d.set_title('Rotating Frame', pad=0)
    
    ax_3d.set_xlim([-1.3, 1.3])
    ax_3d.set_ylim([-1.3, 1.3])
    ax_3d.set_zlim([-1.3, 1.3])
    ax_3d.view_init(elev=20, azim=45)
    ax_3d.set_box_aspect(None, zoom=1.6)
    ax_3d.set_axis_off()
    
    ax_3d.plot([-1.3, 1.3], [0, 0], [0, 0], color='gray', lw=1, linestyle='--')
    ax_3d.plot([0, 0], [-1.3, 1.3], [0, 0], color='gray', lw=1, linestyle='--')
    ax_3d.plot([0, 0], [0, 0], [-1.3, 1.3], color='gray', lw=1, linestyle='--')
    
    ax_3d.text(1.4, 0, 0, 'Mx', color='black', fontsize=10)
    ax_3d.text(0, 1.4, 0, 'My', color='black', fontsize=10)
    ax_3d.text(0, 0, 1.4, 'Mz', color='black', fontsize=10)

    return fig, (ax_seq, ax_mz, ax_3d)

def draw_pulse_sequence(ax, t_180, ti, t_90, t_total):
    ax.plot([0, t_total], [0, 0], color='black', lw=1.5)
    
    ax.add_patch(patches.Rectangle((0, 0), t_180, 1.0, facecolor='black'))
    ax.text(t_180/2, 1.1, '180°', ha='center', fontsize=12)
    
    ax.text(t_180 + ti/2, 0.2, r'$\tau$', ha='center', fontsize=14)
    
    t_90_start = t_180 + ti
    ax.add_patch(patches.Rectangle((t_90_start, 0), t_90, 0.5, facecolor='black'))
    ax.text(t_90_start + t_90/2, 0.6, '90°', ha='center', fontsize=12)
    
    aq_start = t_90_start + t_90
    ax.annotate('', xy=(t_total, -0.2), xytext=(aq_start, -0.2), arrowprops=dict(arrowstyle="->", lw=1.5))
    ax.text((aq_start + t_total)/2, -0.4, 'AQ', ha='center', fontsize=12)
    
    ax.set_xlim([-0.1, t_total + 0.1])
    ax.set_ylim([-0.6, 1.5])
    
    indicator, = ax.plot([], [], color='red', lw=2, linestyle=':')
    return indicator

def render_video(csv_path, output_path, t_180, ti, t_90):
    df = pd.read_csv(csv_path)
    t_total = df['Time'].max()
    
    skip_frames = max(len(df) // 200, 1)
    df = df.iloc[::skip_frames].reset_index(drop=True)
    
    fig, (ax_seq, ax_mz, ax_3d) = setup_ir_dashboard()
    
    seq_indicator = draw_pulse_sequence(ax_seq, t_180, ti, t_90, t_total)
    ax_mz.set_xlim([-0.1, t_total + 0.1])
    
    line_mz, = ax_mz.plot([], [], lw=2, color='orange')
    dot_mz, = ax_mz.plot([], [], 'ro')

    def update(frame):
        while ax_3d.collections:
            ax_3d.collections[0].remove()
            
        t = df['Time'].iloc[frame]
        mz = df['Mz'].iloc[frame]
        mx_rot = df['Mx_rot'].iloc[frame]
        my_rot = df['My_rot'].iloc[frame]
        
        seq_indicator.set_data([t, t], [-0.5, 1.2])
        line_mz.set_data(df['Time'].iloc[:frame], df['Mz'].iloc[:frame])
        dot_mz.set_data([t], [mz])
        
        ax_3d.quiver(0, 0, 0, mx_rot, my_rot, mz, color='red', lw=3, length=1.2, arrow_length_ratio=0.15)
        
        return seq_indicator, line_mz, dot_mz
        
    ani = animation.FuncAnimation(fig, update, frames=len(df), interval=50, blit=False)
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    try:
        ani.save(output_path, fps=20)
        print(f"Success: Video saved to {output_path}")
    except Exception:
        print("FFmpeg not found. Falling back to GIF...")
        fallback_path = output_path.replace('.mp4', '.gif')
        ani.save(fallback_path, writer='pillow', fps=20)
        print(f"Success: GIF saved to {fallback_path}")