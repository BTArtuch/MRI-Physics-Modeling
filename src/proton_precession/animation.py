import matplotlib as mpl
import imageio_ffmpeg
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, FFMpegWriter, PillowWriter

from proton_precession.simulation import SimulationResult
from proton_precession.plotting import (
    create_static_scene,
    draw_oriented_proton_sphere,
    draw_dipole_arrow,
    draw_spin_axis,
    draw_surface_spin_arrows,
    draw_dipole_trail,
)
from proton_precession.persistence.paths import video_path, gif_path


mpl.rcParams["animation.ffmpeg_path"] = imageio_ffmpeg.get_ffmpeg_exe()


class ProtonPrecessionAnimator:
    """
    Builds and optionally saves an animation of proton spin and dipole precession.
    """

    def __init__(self, result: SimulationResult):
        self.result = result
        self.config = result.config

        self.fig = None
        self.ax = None
        self.animation = None

        self.dynamic_artists = []

    def _clear_dynamic_artists(self) -> None:
        """
        Remove artists that change each frame.
        """

        for artist in self.dynamic_artists:
            try:
                artist.remove()
            except ValueError:
                # Artist may already have been removed.
                pass
            except AttributeError:
                # Some artist containers behave differently.
                pass

        self.dynamic_artists = []

    def _draw_dynamic_frame(self, frame_index: int):
        """
        Draw all frame-dependent visual elements.
        """

        dipole_vector = self.result.dipole_vectors[frame_index]
        marker_points = self.result.surface_marker_points[frame_index]
        spin_phase = self.result.spin_phases[frame_index]

        proton_sphere = draw_oriented_proton_sphere(
            self.ax,
            self.config,
            dipole_vector,
            spin_phase,
        )

        dipole_arrow = draw_dipole_arrow(
            self.ax,
            dipole_vector,
            color="red",
        )

        spin_axis = draw_spin_axis(
            self.ax,
            dipole_vector,
            self.config,
        )

        spin_arrows = draw_surface_spin_arrows(
            self.ax,
            marker_points,
            dipole_vector,
            arrow_length=0.32 * self.config.proton_radius,
        )

        trail = draw_dipole_trail(
            ax=self.ax,
            dipole_tips=self.result.dipole_tips,
            frame_index=frame_index,
            trail_length_frames=self.config.trail_length_frames,
        )

        self.dynamic_artists.extend(
            [
                proton_sphere,
                dipole_arrow,
                spin_axis,
            ]
        )

        self.dynamic_artists.extend(spin_arrows)

        if trail is not None:
            self.dynamic_artists.append(trail)

        t = self.result.times[frame_index]
        self.ax.set_title(
            f"Proton Spin and Magnetic Dipole Precession\n"
            f"Frame {frame_index + 1}/{self.config.total_frames} | "
            f"t = {t:.3f} s"
        )

        return self.dynamic_artists
    
    def _init_animation(self):
        """
        Initialize the animation.
        """

        self._clear_dynamic_artists()
        return self._draw_dynamic_frame(0)

    def _update_animation(self, frame_index: int):
        """
        Update function called by Matplotlib FuncAnimation.
        """

        self._clear_dynamic_artists()
        return self._draw_dynamic_frame(frame_index)

    def build(self):
        """
        Build the Matplotlib animation object.
        """

        self.fig, self.ax = create_static_scene(self.config)

        interval_ms = 1000.0 / self.config.fps

        self.animation = FuncAnimation(
            self.fig,
            self._update_animation,
            frames=self.config.total_frames,
            init_func=self._init_animation,
            interval=interval_ms,
            blit=False,
            repeat=True,
        )

        return self.animation

    def save_mp4(self) -> None:
        """
        Save animation as MP4.
        """

        if self.animation is None:
            self.build()

        path = video_path(self.config.output_name)

        ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        mpl.rcParams["animation.ffmpeg_path"] = ffmpeg_exe

        print()
        print(f"Using FFmpeg:")
        print(ffmpeg_exe)

        print()
        print(f"Saving MP4 to:")
        print(path)

        writer = FFMpegWriter(
            fps=self.config.fps,
            metadata={
                "title": "Proton Precession",
                "artist": "mri_physics",
            },
            bitrate=2400,
        )

        self.animation.save(str(path), writer=writer)

        print("MP4 saved.")

    def save_gif(self) -> None:
        """
        Save animation as GIF.
        """

        if self.animation is None:
            self.build()

        path = gif_path(self.config.output_name)

        print()
        print(f"Saving GIF to:")
        print(path)

        writer = PillowWriter(fps=self.config.fps)
        self.animation.save(str(path), writer=writer)

        print("GIF saved.")

    def show(self) -> None:
        """
        Show the animation interactively.
        """

        if self.animation is None:
            self.build()

        plt.show()

    def run(self) -> None:
        """
        Save and/or show the animation according to config.
        """

        if self.animation is None:
            self.build()

        if self.config.save_video:
            self.save_mp4()

        if self.config.save_gif:
            self.save_gif()

        if self.config.show_interactive:
            self.show()
        else:
            plt.close(self.fig)