import matplotlib as mpl
import imageio_ffmpeg
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, FFMpegWriter, PillowWriter

from proton_precession.config import SimulationConfig
from proton_precession.simulation import run_simulation
from proton_precession.plotting import (
    configure_3d_axes,
    draw_reference_axes,
    draw_b0_field,
    draw_precession_cone,
    draw_oriented_proton_sphere,
    draw_dipole_arrow,
    draw_spin_axis,
    draw_surface_spin_arrows,
    draw_dipole_trail,
)
from proton_precession.persistence.paths import video_path, gif_path


mpl.rcParams["animation.ffmpeg_path"] = imageio_ffmpeg.get_ffmpeg_exe()


PROTON_GYROMAGNETIC_RATIO_HZ_PER_T = 42.57747892e6


class LarmorComparisonAnimator:
    """
    Three-panel comparison showing Larmor frequency increasing with B0.

    Panels:
    - 1 T
    - 3 T
    - 7 T

    The true Larmor frequencies are displayed, while the animation uses
    scaled visual frequencies.
    """

    def __init__(
        self,
        base_config,
        b0_values_tesla=(1.0, 3.0, 7.0),
        reference_b0_tesla=1.0,
        reference_visual_frequency_hz=0.10,
        output_name="larmor_b0_comparison",
    ):
        self.base_config = base_config
        self.b0_values_tesla = tuple(b0_values_tesla)
        self.reference_b0_tesla = float(reference_b0_tesla)
        self.reference_visual_frequency_hz = float(reference_visual_frequency_hz)
        self.output_name = output_name

        reference_real_hz = (
            PROTON_GYROMAGNETIC_RATIO_HZ_PER_T * self.reference_b0_tesla
        )
        self.visual_frequency_scale = (
            self.reference_visual_frequency_hz / reference_real_hz
        )

        self.configs = []
        self.results = []
        self.real_larmor_hz = []
        self.visual_larmor_hz = []

        self.fig = None
        self.axes = None
        self.animation = None
        self.bottom_text = None
        self.dynamic_artists = []
        self.sphere_meshes = []

    def prepare_simulations(self):
        self.configs = []
        self.results = []
        self.real_larmor_hz = []
        self.visual_larmor_hz = []

        for b0 in self.b0_values_tesla:
            real_larmor_hz = PROTON_GYROMAGNETIC_RATIO_HZ_PER_T * b0
            visual_precession_hz = real_larmor_hz * self.visual_frequency_scale

            print(
                f"B0 = {b0:.1f} T | "
                f"real f0 = {real_larmor_hz / 1e6:.3f} MHz | "
                f"visual f = {visual_precession_hz:.3f} Hz"
            )

            self.real_larmor_hz.append(real_larmor_hz)
            self.visual_larmor_hz.append(visual_precession_hz)

            config = self.base_config.model_copy(
                update={
                    "precession_frequency_hz": visual_precession_hz,
                }
            )

            self.configs.append(config)
            self.results.append(run_simulation(config))

    def _draw_b0_field_for_panel(self, ax, config: SimulationConfig, b0_tesla: float):
        """
        Draw B0 arrow for a panel.

        Thickness scales mildly with B0.
        """

        L = config.axis_length

        linewidth = 1.8 + 0.45 * b0_tesla
        linewidth = min(max(linewidth, 1.8), 5.5)

        arrow = ax.quiver(
            0,
            0,
            -0.25 * L,
            0,
            0,
            1.0 * L,
            color="blue",
            linewidth=linewidth,
            arrow_length_ratio=0.08,
        )

        ax.text(
            -0.2,
            0.2,
            config.axis_length * 0.70,
            r"$B_0$",
            color="blue",
            fontsize=10,
            ha="left",
            va="bottom",
        )

        return arrow

    def _configure_panel(self, ax, config, b0, panel_index):
        configure_3d_axes(ax, config)
        draw_reference_axes(ax, config)
        self._draw_b0_field_for_panel(ax, config, b0)

        real_mhz = self.real_larmor_hz[panel_index] / 1e6

        ax.text2D(
            0.5,
            1.02,
            rf"$B_0 = {b0:.0f}\,\mathrm{{T}}$",
            transform=ax.transAxes,
            ha="center",
            va="top",
            fontsize=13,
        )

        ax.text2D(
            0.5,
            0.96,
            rf"$f_0 = {real_mhz:.2f}\,\mathrm{{MHz}}$",
            transform=ax.transAxes,
            ha="center",
            va="top",
            fontsize=11,
        )

    def build(self):
        """
        Build the three-panel animation.
        """

        self.prepare_simulations()

        self.fig = plt.figure(figsize=(16, 6))
        self.axes = [
            self.fig.add_subplot(1, 3, i + 1, projection="3d")
            for i in range(3)
        ]

        self.dynamic_artists_by_axis = [[] for _ in self.axes]

        for panel_index, (ax, config, b0) in enumerate(
            zip(self.axes, self.configs, self.b0_values_tesla)
        ):
            self._configure_panel(ax, config, b0, panel_index)

        interval_ms = 1000.0 / self.base_config.fps

        self.animation = FuncAnimation(
            self.fig,
            self._update_animation,
            frames=self.base_config.total_frames,
            init_func=self._init_animation,
            interval=interval_ms,
            blit=False,
            repeat=True,
        )

        # Leave room at the bottom for the global title/time caption.
        self.fig.subplots_adjust(
            left=0.02,
            right=0.98,
            top=0.92,
            bottom=0.01,
            wspace=0.02,
        )

        self.bottom_text = self.fig.text(
            0.5,
            0.2,
            "Larmor Frequency Increases with Magnetic Field Strength",
            ha="center",
            va="bottom",
            fontsize=15,
            fontweight="bold",
        )

        return self.animation

    def _clear_dynamic_artists(self) -> None:
        """
        Clear dynamic artists from all panels.
        """

        for artists in self.dynamic_artists_by_axis:
            for artist in artists:
                try:
                    artist.remove()
                except ValueError:
                    pass
                except AttributeError:
                    pass

            artists.clear()

    def _init_animation(self):
        """
        Initialize the animation.
        """

        self._clear_dynamic_artists()
        return self._draw_frame(0)

    def _update_animation(self, frame_index: int):
        """
        Update animation frame.
        """

        self._clear_dynamic_artists()
        return self._draw_frame(frame_index)

    def _draw_frame(self, frame_index: int):
        """
        Draw all dynamic artists for each B0 panel.
        """

        all_artists = []

        for panel_index, (ax, config, result) in enumerate(
            zip(self.axes, self.configs, self.results)
        ):
            dipole_vector = result.dipole_vectors[frame_index]
            marker_points = result.surface_marker_points[frame_index]
            spin_phase = result.spin_phases[frame_index]

            proton_sphere = draw_oriented_proton_sphere(
                ax,
                config,
                dipole_vector,
                spin_phase,
            )

            dipole_arrow = draw_dipole_arrow(
                ax,
                dipole_vector,
                color="red",
            )

            spin_axis = draw_spin_axis(
                ax,
                dipole_vector,
                config,
            )

            spin_arrows = draw_surface_spin_arrows(
                ax,
                marker_points,
                dipole_vector,
                arrow_length=0.32 * config.proton_radius,
            )

            trail = draw_dipole_trail(
                ax=ax,
                dipole_tips=result.dipole_tips,
                frame_index=frame_index,
                trail_length_frames=config.trail_length_frames,
            )

            artists = [
                proton_sphere,
                dipole_arrow,
                spin_axis,
            ]

            artists.extend(spin_arrows)

            if trail is not None:
                artists.append(trail)

            self.dynamic_artists_by_axis[panel_index].extend(artists)
            all_artists.extend(artists)

        t = self.results[0].times[frame_index]

        if self.bottom_text is not None:
            self.bottom_text.set_text(
                r"Larmor Frequency Increases with Magnetic Field Strength"
                f"    |    t = {t:.3f} s"
                "\n"
                r"$\omega_0 = \gamma B_0$"
                r"    ,    "
                r"$f_0 = \frac{\gamma B_0}{2\pi}$"
            )

        return all_artists

    def save_mp4(self) -> None:
        """
        Save the comparison animation as MP4.
        """

        if self.animation is None:
            self.build()

        path = video_path(self.output_name)

        print()
        print(f"Using FFmpeg:")
        print(imageio_ffmpeg.get_ffmpeg_exe())

        print()
        print(f"Saving comparison MP4 to:")
        print(path)

        writer = FFMpegWriter(
            fps=self.base_config.fps,
            metadata={
                "title": "Larmor B0 Comparison",
                "artist": "mri_physics",
            },
            bitrate=3000,
        )

        self.animation.save(str(path), writer=writer)

        print("Comparison MP4 saved.")

    def save_gif(self) -> None:
            """
            Save animation as GIF.
            """
    
            if self.animation is None:
                self.build()
    
            path = gif_path(self.output_name)
    
            print()
            print(f"Saving GIF to:")
            print(path)
    
            writer = PillowWriter(fps=self.base_config.fps)
            self.animation.save(str(path), writer=writer)
    
            print("GIF saved.")

    def show(self) -> None:
        """
        Show the comparison animation interactively.
        """

        if self.animation is None:
            self.build()

        plt.show()

    def run(self, save_video: bool = False, save_gif: bool = True, show_interactive: bool = True) -> None:
        """
        Run the comparison animation.
        """

        if self.animation is None:
            self.build()

        if save_video:
            self.save_mp4()

        if save_gif:
            self.save_gif()

        if show_interactive:
            self.show()
        else:
            plt.close(self.fig)