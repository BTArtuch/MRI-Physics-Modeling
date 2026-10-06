from pathlib import Path
from pydantic import BaseModel, Field, field_validator


class SimulationConfig(BaseModel):
    """
    Configuration for the proton spin/precession animation.

    This config describes a simplified visualization model:
    - The magnetic dipole precesses around the z-axis.
    - The proton can also spin around its own axis.
    """

    # General simulation timing
    duration_seconds: float = Field(
        default=6.0,
        gt=0.0,
        description="Total animation duration in seconds."
    )

    fps: int = Field(
        default=60,
        gt=0,
        description="Frames per second for the animation."
    )

    # Motion parameters
    precession_frequency_hz: float = Field(
        default=1.0,
        ge=0.0,
        description="Dipole precession frequency around the z-axis in Hz."
    )

    spin_frequency_hz: float = Field(
        default=8.0,
        ge=0.0,
        description="Visual spin frequency of the proton about its own axis in Hz."
    )

    dipole_tilt_degrees: float = Field(
        default=30.0,
        ge=0.0,
        le=180.0,
        description="Angle between magnetic dipole vector and positive z-axis."
    )

    # Visual parameters
    proton_radius: float = Field(
        default=1.0,
        gt=0.0,
        description="Radius of the visualized proton sphere."
    )

    dipole_length: float = Field(
        default=2.0,
        gt=0.0,
        description="Length of the magnetic dipole arrow."
    )

    axis_length: float = Field(
        default=2.5,
        gt=0.0,
        description="Length of displayed reference axes."
    )

    trail_length_frames: int = Field(
        default=120,
        ge=0,
        description="Number of frames to show in the dipole precession trail."
    )

    spin_arrow_count: int = Field(
        default=3,
        ge=1,
        le=12,
        description="Number of surface arrows showing axial spin direction."
    )

    zoom_factor: float = Field(
        default=0.78,
        gt=0.1,
        le=2.0,
        description="Scene zoom factor. Smaller values zoom in."
    )

    show_grid: bool = Field(
        default=False,
        description="Whether to show 3D grid lines."
    )

    show_axis_ticks: bool = Field(
        default=False,
        description="Whether to show numeric axis ticks."
    )

    show_background_panes: bool = Field(
        default=False,
        description="Whether to show Matplotlib 3D background panes/walls."
    )

    # Output
    output_name: str = Field(
        default="proton_precession",
        min_length=1,
        description="Base filename for generated outputs."
    )

    save_video: bool = Field(
        default=False,
        description="Whether to save an MP4 video."
    )

    save_gif: bool = Field(
        default=True,
        description="Whether to save a GIF."
    )

    show_interactive: bool = Field(
        default=True,
        description="Whether to show the animation interactively."
    )

    show_axis_labels: bool = Field(
        default=True,
        description="Whether to show x/y/z axis labels."
    )

    @property
    def total_frames(self) -> int:
        return int(self.duration_seconds * self.fps)

    @property
    def time_step_seconds(self) -> float:
        return 1.0 / self.fps

    @field_validator("output_name")
    @classmethod
    def validate_output_name(cls, value: str) -> str:
        """
        Keep output names filesystem-friendly.
        """
        value = value.strip()

        invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
        for char in invalid_chars:
            if char in value:
                raise ValueError(f"output_name cannot contain '{char}'")

        return value


class RunMetadata(BaseModel):
    """
    Metadata for a saved simulation/render run.
    """

    run_id: str
    config: SimulationConfig
    video_path: str | None = None
    gif_path: str | None = None
    notes: str | None = None