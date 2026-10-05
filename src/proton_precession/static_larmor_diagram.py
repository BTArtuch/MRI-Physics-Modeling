from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt

from proton_precession.config import SimulationConfig
from proton_precession.plotting import configure_3d_axes
from proton_precession.persistence.paths import IMAGE_DIR, ensure_project_directories


def draw_double_cone(ax, cone_height: float, cone_radius: float):
    theta = np.linspace(0.0, 2.0 * np.pi, 160)
    z_up = np.linspace(0.0, cone_height, 80)
    z_down = np.linspace(-cone_height, 0.0, 80)

    theta_grid_up, z_grid_up = np.meshgrid(theta, z_up)
    theta_grid_down, z_grid_down = np.meshgrid(theta, z_down)

    r_up = (cone_radius / cone_height) * z_grid_up
    r_down = (cone_radius / cone_height) * (-z_grid_down)

    x_up = r_up * np.cos(theta_grid_up)
    y_up = r_up * np.sin(theta_grid_up)

    x_down = r_down * np.cos(theta_grid_down)
    y_down = r_down * np.sin(theta_grid_down)

    ax.plot_surface(
        x_up,
        y_up,
        z_grid_up,
        color="red",
        alpha=0.10,
        linewidth=0,
        shade=False,
    )

    ax.plot_surface(
        x_down,
        y_down,
        z_grid_down,
        color="red",
        alpha=0.03,
        linewidth=0,
        shade=False,
    )

    rim_theta = np.linspace(0.0, 2.0 * np.pi, 300)

    ax.plot(
        cone_radius * np.cos(rim_theta),
        cone_radius * np.sin(rim_theta),
        cone_height * np.ones_like(rim_theta),
        color="red",
        linewidth=2.0,
        alpha=0.7,
    )

    ax.plot(
        cone_radius * np.cos(rim_theta),
        cone_radius * np.sin(rim_theta),
        -cone_height * np.ones_like(rim_theta),
        color="red",
        linewidth=2.0,
        alpha=0.7,
    )

def draw_cone_moment_vectors(
    ax,
    cone_height: float,
    cone_radius: float,
    count: int = 10,
    include_lower: bool = True,
):
    angles = np.linspace(0.0, 2.0 * np.pi, count, endpoint=False)

    for theta in angles:
        x = cone_radius * np.cos(theta)
        y = cone_radius * np.sin(theta)
        z = cone_height

        ax.quiver(
            0.0,
            0.0,
            0.0,
            x,
            y,
            z,
            color="red",
            linewidth=1.8,
            alpha=0.55,
            arrow_length_ratio=0.08,
        )

    if include_lower:
        for theta in angles:
            x = cone_radius * np.cos(theta)
            y = cone_radius * np.sin(theta)
            z = -cone_height

            ax.plot(
                [0.0, x],
                [0.0, y],
                [0.0, z],
                color="red",
                linewidth=2.0,
                alpha=0.9,
            )

            vx, vy, vz = x, y, z
            vnorm = np.sqrt(vx**2 + vy**2 + vz**2)
            ux, uy, uz = vx / vnorm, vy / vnorm, vz / vnorm

            ref = np.array([1.0, 0.0, 0.0])
            uvec = np.array([ux, uy, uz])

            perp = np.cross(uvec, ref)
            if np.linalg.norm(perp) < 1e-8:
                ref = np.array([0.0, 1.0, 0.0])
                perp = np.cross(uvec, ref)

            perp = perp / np.linalg.norm(perp)

            head_len = 0.22
            head_width = 0.10

            tip = np.array([x, y, z])
            base = tip - head_len * uvec

            wing1 = base + head_width * perp
            wing2 = base - head_width * perp

            ax.plot(
                [tip[0], wing1[0]],
                [tip[1], wing1[1]],
                [tip[2], wing1[2]],
                color="red",
                linewidth=1.8,
                alpha=0.9,
            )

            ax.plot(
                [tip[0], wing2[0]],
                [tip[1], wing2[1]],
                [tip[2], wing2[2]],
                color="red",
                linewidth=1.8,
                alpha=0.9,
            )


def draw_highlighted_moment(
    ax,
    cone_height: float,
    cone_radius: float,
    theta: float = 0.9,
):
    x = cone_radius * np.cos(theta)
    y = cone_radius * np.sin(theta)
    z = cone_height

    ax.quiver(
        0.0,
        0.0,
        0.0,
        x,
        y,
        z,
        color="black",
        linewidth=3.2,
        alpha=1.0,
        arrow_length_ratio=0.10,
    )

    ax.text(
        x * 1.06,
        y * 1.06,
        z * 1.02,
        r"$\boldsymbol{\mu}_i=\gamma\hbar\mathbf{I}$",
        color="black",
        fontsize=14,
        ha="left",
        va="bottom",
    )


def draw_z_axis(ax, length: float):
    ax.plot(
        [0.0, 0.0],
        [0.0, 0.0],
        [-length, length],
        color="black",
        linewidth=1.8,
        alpha=0.9,
    )

    ax.text(
        0.0,
        0.0,
        length + 0.18,
        r"$+z$",
        color="black",
        fontsize=12,
        ha="center",
        va="bottom",
    )

    ax.text(
        0.0,
        0.0,
        -length - 0.18,
        r"$-z$",
        color="black",
        fontsize=12,
        ha="center",
        va="top",
    )


def draw_m0_vector(ax, length: float):
    ax.quiver(
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        1.25 * length,
        color="darkgreen",
        linewidth=3.0,
        arrow_length_ratio=0.08,
    )

    ax.text(
        0.08,
        0.02,
        1.25 * length + 0.04,
        r"$M_0$",
        color="darkgreen",
        fontsize=14,
        ha="left",
        va="bottom",
    )


def draw_offset_b0_vector(ax, x_offset: float, length: float):
    ax.quiver(
        x_offset,
        0.0,
        -0.1,
        0.0,
        0.0,
        length,
        color="blue",
        linewidth=3.0,
        arrow_length_ratio=0.08,
    )

    ax.text(
        x_offset + 0.08,
        0.0,
        length - 0.02,
        r"$B_0$",
        color="blue",
        fontsize=14,
        ha="left",
        va="bottom",
    )


def create_static_larmor_diagram(config: SimulationConfig):
    fig = plt.figure(figsize=(8, 8))
    ax = fig.add_subplot(111, projection="3d")

    configure_3d_axes(ax, config)

    cone_height = 2.0
    cone_radius = 1.0
    z_axis_length = 2.45

    draw_double_cone(ax, cone_height=cone_height, cone_radius=cone_radius)

    draw_cone_moment_vectors(
        ax,
        cone_height=cone_height,
        cone_radius=cone_radius,
        count=10,
        include_lower=True,
    )

    draw_highlighted_moment(
        ax,
        cone_height=cone_height,
        cone_radius=cone_radius,
        theta=0.95,
    )

    draw_z_axis(ax, length=z_axis_length)
    draw_m0_vector(ax, length=1.90)
    draw_offset_b0_vector(ax, x_offset=1.30, length=1.95)

    ax.set_xlim(-1.55, 1.85)
    ax.set_ylim(-1.35, 1.35)
    ax.set_zlim(-2.35, 2.35)
    ax.set_box_aspect((1, 1, 1.55))
    ax.set_proj_type("ortho")
    ax.view_init(elev=16, azim=-58)

    fig.subplots_adjust(left=0.02, right=0.98, bottom=0.02, top=0.98)
    return fig, ax


def main():
    ensure_project_directories()

    config = SimulationConfig(
        duration_seconds=6.0,
        fps=30,
        precession_frequency_hz=1.0,
        spin_frequency_hz=1.0,
        dipole_tilt_degrees=30.0,
        proton_radius=1.0,
        dipole_length=2.0,
        axis_length=2.5,
        trail_length_frames=60,
        output_name="static_larmor_diagram_clean",
        save_video=False,
        save_gif=False,
        show_interactive=True,
        zoom_factor=0.85,
        show_grid=False,
        show_axis_ticks=False,
        show_background_panes=False,
        spin_arrow_count=3,
    )

    fig, _ = create_static_larmor_diagram(config)

    output_path = IMAGE_DIR / "static_larmor_diagram_clean.png"
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"Saved static diagram to: {output_path}")

    plt.show()


if __name__ == "__main__":
    main()