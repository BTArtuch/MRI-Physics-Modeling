from proton_precession.config import SimulationConfig
from proton_precession.persistence.paths import (
    ensure_project_directories,
    config_path,
    export_path,
)
from proton_precession.persistence.json_store import (
    save_model_json,
    load_model_json,
)
from proton_precession.persistence.csv_store import save_simulation_vectors_csv
from proton_precession.simulation import run_simulation
from proton_precession.animation import ProtonPrecessionAnimator


def create_default_config_if_missing() -> SimulationConfig:
    """
    Create data/configs/default_precession.json if it does not exist.
    Then load and return it.
    """

    path = config_path("default_precession")

    if not path.exists():
        print(f"Creating default config: {path}")
        config = SimulationConfig()
        save_model_json(config, path)
    else:
        print(f"Default config already exists: {path}")

    loaded_config = load_model_json(SimulationConfig, path)
    return loaded_config


def main() -> None:
    ensure_project_directories()

    config = create_default_config_if_missing()

    print()
    print("Loaded simulation config:")
    print(config.model_dump_json(indent=4))

    print()
    print(f"Total frames: {config.total_frames}")
    print(f"Time step: {config.time_step_seconds:.6f} seconds")

    result = run_simulation(config)

    csv_path = export_path(f"{config.output_name}_vectors")
    save_simulation_vectors_csv(result, csv_path)

    print()
    print(f"Saved simulation CSV:")
    print(csv_path)

    animator = ProtonPrecessionAnimator(result)
    animator.run()


if __name__ == "__main__":
    main()