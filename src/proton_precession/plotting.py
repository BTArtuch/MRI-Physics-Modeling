import numpy as np
import matplotlib.pyplot as plt

from mpl_toolkits.mplot3d.art3d import Line3DCollection

from proton_precession.config import SimulationConfig


def set_axes_equal(ax) -> None:
    """
    Set equal scaling for a 3D Matplotlib axis.

    Matplotlib's 3D plots do not naturally use equal aspect ratios.
    This prevents spheres from looking like ellipsoids.
    """

    x_limits = ax.get_xlim3d()
    y_limits = ax.get_ylim3d()
    z_limits = ax.get_zlim3d()

    x_range = abs(x_limits[1] - x_limits[0])
    y_range = abs(y_limits[1] - y_limits[0])
    z_range = abs(z_limits[1] - z_limits[0])

    x_middle = np.mean(x_limits)
    y_middle = np.mean(y_limits)
    z_middle = np.mean(z_limits)

    plot_radius = 0.5 * max([x_range, y_range, z_range])

    ax.set_xlim3d([x_middle - plot_radius, x_middle + plot_radius])
    ax.set_ylim3d([y_middle - plot_radius, y_middle + plot_radius])
    ax.set_zlim3d([z_middle - plot_radius, z_middle + plot_radius])


def configure_3d_axes(ax, config: SimulationConfig) -> None:
    """
    Configure labels, limits, view angle, aspect, and background style.

    Uses symmetric limits, a 1:1:1 box aspect, and orthographic projection
    so the proton sphere renders as a true sphere.
    """

    base_limit = max(
        config.axis_length,
        config.dipole_length,
        config.proton_radius,
    ) * 1.25

    limit = base_limit * config.zoom_factor

    ax.set_xlim(-limit, limit)
    ax.set_ylim(-limit, limit)
    ax.set_zlim(-limit, limit)

    try:
        ax.set_box_aspect((1, 1, 1))
    except AttributeError:
        set_axes_equal(ax)

    ax.set_proj_type("ortho")

    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.set_zlabel("")

    # ax.set_title("Proton Spin and Magnetic Dipole Precession")

    ax.view_init(elev=28, azim=35)

    # Remove background panes/walls.
    if not config.show_background_panes:
        ax.xaxis.pane.set_alpha(0.0)
        ax.yaxis.pane.set_alpha(0.0)
        ax.zaxis.pane.set_alpha(0.0)

        ax.xaxis.pane.set_edgecolor((1, 1, 1, 0))
        ax.yaxis.pane.set_edgecolor((1, 1, 1, 0))
        ax.zaxis.pane.set_edgecolor((1, 1, 1, 0))

    # Remove grid.
    ax.grid(config.show_grid)

    # Remove numeric ticks.
    if not config.show_axis_ticks:
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_zticks([])

    # Hide Matplotlib's remaining 3D box/frame axis lines.
    if not config.show_background_panes:
        try:
            ax.xaxis.line.set_color((1, 1, 1, 0))
            ax.yaxis.line.set_color((1, 1, 1, 0))
            ax.zaxis.line.set_color((1, 1, 1, 0))

            ax.xaxis.line.set_linewidth(0)
            ax.yaxis.line.set_linewidth(0)
            ax.zaxis.line.set_linewidth(0)
        except AttributeError:
            pass


def draw_reference_axes(ax, config: SimulationConfig) -> None:
    """
    Draw x, y, and z coordinate axes.
    """

    L = config.axis_length

    # x-axis
    ax.plot([-L, L], [0, 0], [0, 0], color="gray", linewidth=1)
    ax.text(L, 0, 0, "+x", color="gray")

    # y-axis
    ax.plot([0, 0], [-L, L], [0, 0], color="gray", linewidth=1)
    ax.text(0, L, 0, "+y", color="gray")

    # z-axis
    ax.plot([0, 0], [0, 0], [-0.5 * L, L], color="black", linewidth=1.2)
    ax.text(0, 0, L, "+z", color="black")


def draw_b0_field(ax, config: SimulationConfig):
    """
    Draw the main external magnetic field B0 along +z.
    """

    L = config.axis_length

    arrow = ax.quiver(
        0,
        0,
        -0.45 * L,
        0,
        0,
        1.2 * L,
        color="blue",
        linewidth=2.8,
        arrow_length_ratio=0.08,
        label="B0",
    )

    # Offset the label slightly so it does not overlap the z-axis or cone.
    ax.text(
        0.10 * L,
        -0.10 * L,
        0.75 * L,
        r"$B_0$",
        color="blue",
        fontsize=13,
        fontweight="bold",
    )

    return arrow


def draw_proton_sphere(ax, config: SimulationConfig):
    """
    Draw a translucent proton sphere centered at the origin.
    """

    r = config.proton_radius

    u = np.linspace(0, 2.0 * np.pi, 72)
    v = np.linspace(0, np.pi, 36)

    x = r * np.outer(np.cos(u), np.sin(v))
    y = r * np.outer(np.sin(u), np.sin(v))
    z = r * np.outer(np.ones_like(u), np.cos(v))

    sphere = ax.plot_surface(
        x,
        y,
        z,
        color="lightcoral",
        alpha=0.32,
        linewidth=0.25,
        edgecolor=(0.7, 0.2, 0.2, 0.15),
        shade=True,
        antialiased=True,
    )

    return sphere


def draw_precession_cone(ax, config: SimulationConfig):
    """
    Draw the circular path of the dipole tip and cone guide lines.

    The dipole tip moves around a circle at fixed z.
    """

    theta = np.deg2rad(config.dipole_tilt_degrees)
    L = config.dipole_length

    radius = L * np.sin(theta)
    z = L * np.cos(theta)

    phi = np.linspace(0, 2.0 * np.pi, 240)

    x = radius * np.cos(phi)
    y = radius * np.sin(phi)
    z_values = np.full_like(phi, z)

    circle_line, = ax.plot(
        x,
        y,
        z_values,
        color="orange",
        linestyle="--",
        linewidth=1.2,
        alpha=0.8,
        label="precession path",
    )

    # A few cone guide lines from origin to circle
    for guide_phi in np.linspace(0, 2.0 * np.pi, 8, endpoint=False):
        gx = radius * np.cos(guide_phi)
        gy = radius * np.sin(guide_phi)
        ax.plot(
            [0, gx],
            [0, gy],
            [0, z],
            color="orange",
            linestyle=":",
            linewidth=0.7,
            alpha=0.35,
        )

    return circle_line


def draw_dipole_arrow(ax, dipole_vector: np.ndarray, color: str = "red"):
    """
    Draw magnetic dipole arrow from origin to dipole_vector.
    """

    dipole_vector = np.asarray(dipole_vector, dtype=float)

    arrow = ax.quiver(
        0,
        0,
        0,
        dipole_vector[0],
        dipole_vector[1],
        dipole_vector[2],
        color=color,
        linewidth=3,
        arrow_length_ratio=0.12,
        label="magnetic dipole",
    )

    return arrow


def draw_spin_axis(ax, dipole_vector: np.ndarray, config: SimulationConfig):
    """
    Draw a thinner line through the proton along the dipole/spin axis.

    This visually suggests the proton's own spin axis.
    """

    dipole_vector = np.asarray(dipole_vector, dtype=float)
    unit = dipole_vector / np.linalg.norm(dipole_vector)

    r = config.proton_radius * 1.15

    start = -r * unit
    end = r * unit

    line, = ax.plot(
        [start[0], end[0]],
        [start[1], end[1]],
        [start[2], end[2]],
        color="purple",
        linewidth=2,
        alpha=0.9,
        label="spin axis",
    )

    return line


def draw_surface_spin_arrows(
    ax,
    marker_points: np.ndarray,
    dipole_vector: np.ndarray,
    arrow_length: float = 0.35,
):
    """
    Draw small tangent arrows on the proton surface.

    These arrows replace simple surface marker dots. They point in the local
    direction of rotation about the dipole/spin axis.

    The tangent direction is computed using the right-hand rule:

        tangent = spin_axis x radius_vector

    where radius_vector points from the proton center to the surface point.
    """

    marker_points = np.asarray(marker_points, dtype=float)
    dipole_vector = np.asarray(dipole_vector, dtype=float)

    spin_axis = dipole_vector / np.linalg.norm(dipole_vector)

    artists = []

    for point in marker_points:
        radius_vector = point / np.linalg.norm(point)

        tangent = np.cross(radius_vector, spin_axis)
        tangent_norm = np.linalg.norm(tangent)

        # If the point is accidentally parallel to the axis, skip it.
        if tangent_norm == 0:
            continue

        tangent = tangent / tangent_norm

        arrow = ax.quiver(
            point[0],
            point[1],
            point[2],
            arrow_length * tangent[0],
            arrow_length * tangent[1],
            arrow_length * tangent[2],
            color="black",
            linewidth=2.0,
            arrow_length_ratio=0.45,
            normalize=False,
        )

        artists.append(arrow)

    return artists


def draw_dipole_trail(
    ax,
    dipole_tips: np.ndarray,
    frame_index: int,
    trail_length_frames: int,
):
    """
    Draw recent path of the dipole tip.
    """

    if trail_length_frames <= 0:
        return None

    start_index = max(0, frame_index - trail_length_frames)
    trail = dipole_tips[start_index: frame_index + 1]

    if trail.shape[0] < 2:
        return None

    line, = ax.plot(
        trail[:, 0],
        trail[:, 1],
        trail[:, 2],
        color="red",
        linewidth=2,
        alpha=0.55,
    )

    return line


def create_static_scene(config: SimulationConfig):
    """
    Create a basic static 3D scene with fixed background elements.

    Returns:
        fig, ax
    """

    fig = plt.figure(figsize=(9, 8))
    ax = fig.add_subplot(111, projection="3d")

    configure_3d_axes(ax, config)

    draw_reference_axes(ax, config)
    draw_b0_field(ax, config)
    #draw_proton_sphere(ax, config)
    draw_precession_cone(ax, config)

    return fig, ax

def rotation_matrix_from_vectors(source: np.ndarray, target: np.ndarray) -> np.ndarray:
    """
    Return a rotation matrix that rotates source vector onto target vector.

    Both source and target are treated as 3D vectors.
    """

    source = np.asarray(source, dtype=float)
    target = np.asarray(target, dtype=float)

    source = source / np.linalg.norm(source)
    target = target / np.linalg.norm(target)

    cross = np.cross(source, target)
    dot = np.dot(source, target)

    if np.isclose(dot, 1.0):
        return np.eye(3)

    if np.isclose(dot, -1.0):
        # 180 degree rotation. Pick any perpendicular axis.
        if abs(source[0]) < 0.9:
            axis = np.cross(source, np.array([1.0, 0.0, 0.0]))
        else:
            axis = np.cross(source, np.array([0.0, 1.0, 0.0]))

        axis = axis / np.linalg.norm(axis)
        return rotation_matrix_about_axis(axis, np.pi)

    skew = np.array(
        [
            [0.0, -cross[2], cross[1]],
            [cross[2], 0.0, -cross[0]],
            [-cross[1], cross[0], 0.0],
        ]
    )

    rotation = (
        np.eye(3)
        + skew
        + skew @ skew * ((1.0 - dot) / (np.linalg.norm(cross) ** 2))
    )

    return rotation


def rotation_matrix_about_axis(axis: np.ndarray, angle_radians: float) -> np.ndarray:
    """
    Rodrigues rotation matrix for rotating around an arbitrary 3D axis.
    """

    axis = np.asarray(axis, dtype=float)
    axis = axis / np.linalg.norm(axis)

    x, y, z = axis

    c = np.cos(angle_radians)
    s = np.sin(angle_radians)
    one_minus_c = 1.0 - c

    return np.array(
        [
            [
                c + x * x * one_minus_c,
                x * y * one_minus_c - z * s,
                x * z * one_minus_c + y * s,
            ],
            [
                y * x * one_minus_c + z * s,
                c + y * y * one_minus_c,
                y * z * one_minus_c - x * s,
            ],
            [
                z * x * one_minus_c - y * s,
                z * y * one_minus_c + x * s,
                c + z * z * one_minus_c,
            ],
        ],
        dtype=float,
    )

def draw_oriented_proton_sphere(
    ax,
    config: SimulationConfig,
    dipole_vector: np.ndarray,
    spin_phase_radians: float,
):
    """
    Draw a proton sphere whose local body axis is aligned with the dipole vector.

    The base sphere is generated with its local symmetry axis along +z.
    Then we:
    1. rotate it about local z by the proton spin phase
    2. rotate local z onto the current dipole/precession vector

    This makes the sphere's visible mesh/texture precess with the magnetic
    dipole instead of staying aligned with the lab-frame z axis.
    """

    r = config.proton_radius

    u = np.linspace(0, 2.0 * np.pi, 36)
    v = np.linspace(0, np.pi, 18)

    x = r * np.outer(np.cos(u), np.sin(v))
    y = r * np.outer(np.sin(u), np.sin(v))
    z = r * np.outer(np.ones_like(u), np.cos(v))

    points = np.stack(
        [
            x.ravel(),
            y.ravel(),
            z.ravel(),
        ],
        axis=0,
    )

    dipole_unit = np.asarray(dipole_vector, dtype=float)
    dipole_unit = dipole_unit / np.linalg.norm(dipole_unit)

    local_z = np.array([0.0, 0.0, 1.0])

    # First spin the proton around its own local z-axis.
    spin_rotation = rotation_matrix_about_axis(local_z, spin_phase_radians)

    # Then align the local z-axis with the current dipole vector.
    alignment_rotation = rotation_matrix_from_vectors(local_z, dipole_unit)

    total_rotation = alignment_rotation @ spin_rotation

    rotated_points = total_rotation @ points

    xr = rotated_points[0].reshape(x.shape)
    yr = rotated_points[1].reshape(y.shape)
    zr = rotated_points[2].reshape(z.shape)

    sphere = ax.plot_surface(
        xr,
        yr,
        zr,
        color="lightcoral",
        alpha=0.32,
        linewidth=0.25,
        edgecolor=(0.7, 0.2, 0.2, 0.18),
        shade=True,
        antialiased=True,
    )

    return sphere