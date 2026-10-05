from dataclasses import dataclass

import numpy as np

from proton_precession.config import SimulationConfig


@dataclass
class FrameState:
    """
    Computed state for one animation frame.
    """

    frame_index: int
    time_seconds: float

    dipole_vector: np.ndarray
    dipole_tip: np.ndarray

    spin_phase_radians: float
    precession_phase_radians: float

    surface_marker_points: np.ndarray


@dataclass
class SimulationResult:
    """
    Full computed simulation over all frames.
    """

    config: SimulationConfig
    times: np.ndarray
    dipole_vectors: np.ndarray
    dipole_tips: np.ndarray
    spin_phases: np.ndarray
    precession_phases: np.ndarray
    surface_marker_points: np.ndarray


def unit_vector_from_spherical(theta_radians: float, phi_radians: float) -> np.ndarray:
    """
    Return a 3D unit vector using physics-style spherical coordinates.

    theta is the polar angle from +z.
    phi is the azimuthal angle around z from +x.
    """

    return np.array(
        [
            np.sin(theta_radians) * np.cos(phi_radians),
            np.sin(theta_radians) * np.sin(phi_radians),
            np.cos(theta_radians),
        ],
        dtype=float,
    )


def rotation_matrix_about_axis(axis: np.ndarray, angle_radians: float) -> np.ndarray:
    """
    Rodrigues rotation matrix for rotating around an arbitrary 3D axis.
    """

    axis = np.asarray(axis, dtype=float)
    norm = np.linalg.norm(axis)

    if norm == 0:
        raise ValueError("Rotation axis cannot be the zero vector.")

    x, y, z = axis / norm

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


def make_perpendicular_unit_vector(axis: np.ndarray) -> np.ndarray:
    """
    Return a unit vector perpendicular to the given axis.

    Used to create a visible surface marker on the proton that rotates
    around the spin/dipole axis.
    """

    axis = np.asarray(axis, dtype=float)
    axis = axis / np.linalg.norm(axis)

    # Pick a reference vector that is not parallel to axis.
    if abs(axis[2]) < 0.9:
        reference = np.array([0.0, 0.0, 1.0])
    else:
        reference = np.array([1.0, 0.0, 0.0])

    perpendicular = np.cross(axis, reference)
    perpendicular /= np.linalg.norm(perpendicular)

    return perpendicular


def compute_surface_marker_points(
    dipole_unit_vector: np.ndarray,
    spin_phase_radians: float,
    proton_radius: float,
    marker_count: int = 3,
) -> np.ndarray:
    """
    Compute points on the proton surface that rotate about the dipole axis.

    These points are visual aids. They make the proton sphere look like it is
    spinning around its own magnetic axis.
    """

    dipole_unit_vector = np.asarray(dipole_unit_vector, dtype=float)
    dipole_unit_vector = dipole_unit_vector / np.linalg.norm(dipole_unit_vector)

    base_perpendicular = make_perpendicular_unit_vector(dipole_unit_vector)

    points = []

    for i in range(marker_count):
        phase = spin_phase_radians + i * (2.0 * np.pi / marker_count)
        rotation = rotation_matrix_about_axis(dipole_unit_vector, phase)
        point = rotation @ base_perpendicular
        points.append(proton_radius * point)

    return np.array(points, dtype=float)


def simulate_frame(config: SimulationConfig, frame_index: int) -> FrameState:
    """
    Compute the simulation state for one frame.
    """

    t = frame_index / config.fps

    theta = np.deg2rad(config.dipole_tilt_degrees)

    omega_precession = 2.0 * np.pi * config.precession_frequency_hz
    omega_spin = 2.0 * np.pi * config.spin_frequency_hz

    precession_phase = -omega_precession * t
    spin_phase = -omega_spin * t

    dipole_unit = unit_vector_from_spherical(theta, precession_phase)
    dipole_vector = config.dipole_length * dipole_unit

    surface_marker_points = compute_surface_marker_points(
        dipole_unit_vector=dipole_unit,
        spin_phase_radians=spin_phase,
        proton_radius=config.proton_radius,
        marker_count=config.spin_arrow_count,
    )

    return FrameState(
        frame_index=frame_index,
        time_seconds=t,
        dipole_vector=dipole_vector,
        dipole_tip=dipole_vector,
        spin_phase_radians=spin_phase,
        precession_phase_radians=precession_phase,
        surface_marker_points=surface_marker_points,
    )


def run_simulation(config: SimulationConfig) -> SimulationResult:
    """
    Compute all frames for the animation.
    """

    total_frames = config.total_frames

    times = np.zeros(total_frames, dtype=float)
    dipole_vectors = np.zeros((total_frames, 3), dtype=float)
    dipole_tips = np.zeros((total_frames, 3), dtype=float)
    spin_phases = np.zeros(total_frames, dtype=float)
    precession_phases = np.zeros(total_frames, dtype=float)

    marker_count = config.spin_arrow_count
    surface_marker_points = np.zeros((total_frames, marker_count, 3), dtype=float)

    for frame_index in range(total_frames):
        state = simulate_frame(config, frame_index)

        times[frame_index] = state.time_seconds
        dipole_vectors[frame_index] = state.dipole_vector
        dipole_tips[frame_index] = state.dipole_tip
        spin_phases[frame_index] = state.spin_phase_radians
        precession_phases[frame_index] = state.precession_phase_radians
        surface_marker_points[frame_index] = state.surface_marker_points

    return SimulationResult(
        config=config,
        times=times,
        dipole_vectors=dipole_vectors,
        dipole_tips=dipole_tips,
        spin_phases=spin_phases,
        precession_phases=precession_phases,
        surface_marker_points=surface_marker_points,
    )