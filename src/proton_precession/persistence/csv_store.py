import csv
from pathlib import Path

from proton_precession.simulation import SimulationResult


def save_simulation_vectors_csv(result: SimulationResult, path: Path) -> None:
    """
    Save per-frame simulation vector data to a CSV file.

    This exports:
    - frame index
    - time
    - dipole vector components
    - dipole tip components
    - spin phase
    - precession phase
    - surface spin arrow anchor points
    """

    path.parent.mkdir(parents=True, exist_ok=True)

    marker_count = result.surface_marker_points.shape[1]

    fieldnames = [
        "frame",
        "time_seconds",

        "dipole_x",
        "dipole_y",
        "dipole_z",

        "dipole_tip_x",
        "dipole_tip_y",
        "dipole_tip_z",

        "spin_phase_radians",
        "precession_phase_radians",
    ]

    for marker_index in range(marker_count):
        fieldnames.extend(
            [
                f"marker_{marker_index}_x",
                f"marker_{marker_index}_y",
                f"marker_{marker_index}_z",
            ]
        )

    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        total_frames = result.times.shape[0]

        for frame_index in range(total_frames):
            dipole = result.dipole_vectors[frame_index]
            dipole_tip = result.dipole_tips[frame_index]
            markers = result.surface_marker_points[frame_index]

            row = {
                "frame": frame_index,
                "time_seconds": result.times[frame_index],

                "dipole_x": dipole[0],
                "dipole_y": dipole[1],
                "dipole_z": dipole[2],

                "dipole_tip_x": dipole_tip[0],
                "dipole_tip_y": dipole_tip[1],
                "dipole_tip_z": dipole_tip[2],

                "spin_phase_radians": result.spin_phases[frame_index],
                "precession_phase_radians": result.precession_phases[frame_index],
            }

            for marker_index in range(marker_count):
                row[f"marker_{marker_index}_x"] = markers[marker_index, 0]
                row[f"marker_{marker_index}_y"] = markers[marker_index, 1]
                row[f"marker_{marker_index}_z"] = markers[marker_index, 2]

            writer.writerow(row)