"""Dashboard and video rendering for a spin-echo pulse sequence."""

import math
import os

import matplotlib.animation as animation
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import pandas as pd


def setup_spin_echo_dashboard():
    fig = plt.figure(figsize=(14, 8))
    fig.suptitle("Spin Echo (SE) Pulse Sequence", fontsize=18)

    grid = fig.add_gridspec(
        2, 2, width_ratios=[1.2, 1.0], height_ratios=[1, 1],
        wspace=0.2, hspace=0.3,
    )
    ax_sequence = fig.add_subplot(grid[0, 0])
    ax_sequence.set_title("Pulse Sequence", pad=10)
    ax_sequence.set_axis_off()

    ax_mz = fig.add_subplot(grid[1, 0])
    ax_mz.set_title(r"$T_1$ Longitudinal Relaxation ($M_0$)")
    ax_mz.set_ylim(-1.1, 1.1)
    ax_mz.set_xlabel("Time (s)")
    ax_mz.set_ylabel("Magnitude")
    ax_mz.grid(True)
    ax_mz.axhline(0, color="black", linewidth=1)

    ax_3d = fig.add_subplot(grid[:, 1], projection="3d")
    ax_3d.set_title("Rotating Frame", pad=0)
    ax_3d.set_xlim([-1.3, 1.3])
    ax_3d.set_ylim([-1.3, 1.3])
    ax_3d.set_zlim([-1.3, 1.3])
    ax_3d.view_init(elev=20, azim=45)
    ax_3d.set_box_aspect(None, zoom=1.6)
    ax_3d.set_axis_off()

    ax_3d.plot([-1.3, 1.3], [0, 0], [0, 0], color="gray", lw=1, linestyle="--")
    ax_3d.plot([0, 0], [-1.3, 1.3], [0, 0], color="gray", lw=1, linestyle="--")
    ax_3d.plot([0, 0], [0, 0], [-1.3, 1.3], color="gray", lw=1, linestyle="--")
    ax_3d.text(1.4, 0, 0, "Mx", color="black", fontsize=10)
    ax_3d.text(0, 1.4, 0, "My", color="black", fontsize=10)
    ax_3d.text(0, 0, 1.4, "Mz", color="black", fontsize=10)
    return fig, (ax_sequence, ax_mz, ax_3d)


def draw_pulse_sequence(ax, t_90, te, t_180, t_total):
    pulse_180_start = t_90 + te / 2
    pulse_180_end = pulse_180_start + t_180
    echo_time = pulse_180_end + te / 2

    ax.plot([0, t_total], [0, 0], color="black", lw=1.5)
    ax.add_patch(patches.Rectangle((0, 0), t_90, 0.5, facecolor="black"))
    ax.text(t_90 / 2, 0.6, "90°", ha="center", fontsize=12)
    ax.add_patch(
        patches.Rectangle((pulse_180_start, 0), t_180, 1.0, facecolor="black")
    )
    ax.text((pulse_180_start + pulse_180_end) / 2, 1.1, "180°", ha="center", fontsize=12)

    ax.annotate(
        "", xy=(pulse_180_start, -0.15), xytext=(t_90, -0.15),
        arrowprops=dict(arrowstyle="<->", lw=1),
    )
    ax.text((t_90 + pulse_180_start) / 2, -0.4, r"$\tau$", ha="center", fontsize=12)
    ax.annotate(
        "", xy=(echo_time, -0.15), xytext=(pulse_180_end, -0.15),
        arrowprops=dict(arrowstyle="<->", lw=1),
    )
    ax.text((pulse_180_end + echo_time) / 2, -0.4, r"$\tau$", ha="center", fontsize=12)
    ax.axvline(echo_time, color="tab:green", linestyle=":", linewidth=1.5)
    ax.text(echo_time, 0.75, "Echo", color="tab:green", ha="center", fontsize=10)

    acquisition_start = t_90
    ax.annotate(
        "", xy=(t_total, -0.65), xytext=(acquisition_start, -0.65),
        arrowprops=dict(arrowstyle="->", lw=1.5),
    )
    ax.text((acquisition_start + t_total) / 2, -0.9, "Acquisition", ha="center", fontsize=10)
    ax.set_xlim([-0.05, t_total + 0.05])
    ax.set_ylim([-1.0, 1.5])
    indicator, = ax.plot([], [], color="red", lw=2, linestyle=":")
    return indicator


def render_animation(csv_path, output_path, t_90, te, t_180, max_frames=200):
    if max_frames < 1:
        raise ValueError("max_frames must be positive")
    df = pd.read_csv(csv_path)
    required_columns = {"Time", "Mx", "My", "Mz", "Mxy_net"}
    missing_columns = required_columns.difference(df.columns)
    if missing_columns:
        raise ValueError(f"Trajectory is missing columns: {', '.join(sorted(missing_columns))}")
    if df.empty:
        raise ValueError("Cannot render an empty spin-echo trajectory")

    skip_frames = max(math.ceil(len(df) / max_frames), 1)
    df = df.iloc[::skip_frames].reset_index(drop=True)
    t_total = float(df["Time"].iloc[-1])

    fig, (ax_sequence, ax_mz, ax_3d) = setup_spin_echo_dashboard()
    sequence_indicator = draw_pulse_sequence(ax_sequence, t_90, te, t_180, t_total)
    ax_mz.set_xlim([-0.05, t_total + 0.05])
    mz_line, = ax_mz.plot([], [], lw=2, color="orange")
    mz_dot, = ax_mz.plot([], [], "ro")
    echo_time = t_90 + te + t_180
    ax_mz.axvline(echo_time, color="tab:green", linestyle=":", linewidth=1)

    def update(frame):
        for collection in list(ax_3d.collections):
            collection.remove()

        row = df.iloc[frame]
        time = row["Time"]
        sequence_indicator.set_data([time, time], [-0.95, 1.2])
        mz_line.set_data(df["Time"].iloc[:frame + 1], df["Mz"].iloc[:frame + 1])
        mz_dot.set_data([time], [row["Mz"]])
        ax_3d.quiver(
            0, 0, 0, row["Mx"], row["My"], row["Mz"],
            color="red", lw=3, length=1.2, arrow_length_ratio=0.15,
        )
        pulse_180_start = t_90 + te / 2
        pulse_180_end = pulse_180_start + t_180
        if time <= t_90 or pulse_180_start <= time <= pulse_180_end:
            ax_3d.quiver(
                0, 0, 0, 0.8, 0, 0, color="orange", lw=2,
                length=1.0, arrow_length_ratio=0.15,
            )
        return sequence_indicator, mz_line, mz_dot

    movie = animation.FuncAnimation(
        fig, update, frames=len(df), interval=50, blit=False
    )
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    output_root, _ = os.path.splitext(output_path)
    saved_path = output_root + ".gif"
    movie.save(saved_path, writer="pillow", fps=20)

    plt.close(fig)
    print(f"Animation saved to {saved_path}")
    return saved_path
