from proton_precession.config import SimulationConfig
from proton_precession.persistence.paths import ensure_project_directories, config_path
from proton_precession.persistence.json_store import load_model_json, save_model_json
from proton_precession.comparison_animation import LarmorComparisonAnimator


def load_or_create_base_config() -> SimulationConfig:
    """
    Load the default config, or create it if missing.
    """

    path = config_path("default_precession")

    if not path.exists():
        config = SimulationConfig()
        save_model_json(config, path)
        return config

    return load_model_json(SimulationConfig, path)


def main() -> None:
    ensure_project_directories()

    base_config = load_or_create_base_config()

    # Recommended settings for side-by-side comparison.
    # We override only the values needed for this visualization.
    base_config = base_config.model_copy(
        update={
            "duration_seconds": 15.0,
            "fps": 20,
            "spin_frequency_hz": 0.75,
            "trail_length_frames": 45,
            "spin_arrow_count": 3,
            "zoom_factor": 0.60,
            "save_video": True,
            "show_interactive": True,
        }
    )

    animator = LarmorComparisonAnimator(
        base_config=base_config,
        b0_values_tesla=(1.0, 3.0, 7.0),
        reference_b0_tesla=1.0,
        reference_visual_frequency_hz=0.10,
        output_name="larmor_b0_comparison",
    )

    animator.run(
        save_video=True,
        show_interactive=True,
    )


if __name__ == "__main__":
    main()