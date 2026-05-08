"""Animate a chain of rotating arms and save the completed traced pattern."""

from dataclasses import dataclass, field
import json
import pathlib

import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np


START_TOLERANCE = 1e-2
MIN_FRAMES_BEFORE_CLOSE_CHECK = 10


@dataclass
class FourierState:
    """Mutable animation state for a Fourier arm chain."""

    angles: np.ndarray
    lengths: np.ndarray
    speeds: np.ndarray
    pattern_points_x: list[float] = field(default_factory=list)
    pattern_points_y: list[float] = field(default_factory=list)

    @property
    def arm_count(self):
        """Return the number of complete arm definitions available."""

        return min(len(self.angles), len(self.lengths), len(self.speeds))


@dataclass
class FourierArtists:
    """Matplotlib objects updated by the animation loop."""

    fig: object
    ax: object
    trail_line: object
    line: object
    final_dot: object


def load_config(config_path="config.json"):
    """Load arm angles, lengths, and speeds from a JSON config file."""

    cfg = json.loads(pathlib.Path(config_path).read_text())
    return FourierState(
        angles=np.array(cfg["angles"], dtype=float),
        lengths=np.array(cfg["lengths"], dtype=float),
        speeds=np.array(cfg["speeds"], dtype=float),
    )


def create_figure():
    """Create and configure the figure used to render the arm animation."""

    fig, ax = plt.subplots()
    (trail_line,) = ax.plot([], [], marker="o", color="black", markersize=1)
    (line,) = ax.plot([], [], marker="o", color="orange", markersize=3)
    (final_dot,) = ax.plot([], [], "rx")

    ax.set_xlim(-30, 30)
    ax.set_ylim(-30, 30)
    ax.set_aspect("equal")
    ax.grid()
    ax.spines["left"].set_position("zero")
    ax.spines["bottom"].set_position("zero")
    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)

    return FourierArtists(
        fig=fig,
        ax=ax,
        trail_line=trail_line,
        line=line,
        final_dot=final_dot,
    )


def compute_points(angles, lengths, arm_count=None):
    """
    Return the joint coordinates for the current arm chain.

    The first point is the origin; each following point is the end of one arm.
    """

    if arm_count is None:
        arm_count = min(len(angles), len(lengths))

    x_index = [0] + [
        sum(
            lengths[i] * np.cos(np.radians(angles[i] % 360))
            for i in range(j + 1)
        )
        for j in range(arm_count)
    ]

    y_index = [0] + [
        sum(
            lengths[i] * np.sin(np.radians(angles[i] % 360))
            for i in range(j + 1)
        )
        for j in range(arm_count)
    ]

    return x_index, y_index


def save_pattern(pattern_points_x, pattern_points_y, output_dir="output"):
    """Save the traced endpoint coordinates and the current figure image."""

    pathlib.Path(output_dir).mkdir(parents=True, exist_ok=True)
    with open(pathlib.Path(output_dir) / "pattern_points.txt", "w") as f:
        for x, y in zip(pattern_points_x, pattern_points_y):
            f.write(f"{x}, {y}\n")
    plt.savefig(pathlib.Path(output_dir) / "Ending_Pattern.png")


def update(frame, state, artists):
    """
    Advance the animation by one frame and update the plotted artists.

    The frame number is supplied by matplotlib but is not needed here.
    """

    for i in range(state.arm_count):
        state.angles[i] += state.speeds[i]
        state.angles[i] = state.angles[i] % 360

    x_index, y_index = compute_points(state.angles, state.lengths, state.arm_count)

    state.pattern_points_x.append(x_index[-1])
    state.pattern_points_y.append(y_index[-1])

    artists.trail_line.set_data(state.pattern_points_x, state.pattern_points_y)

    artists.line.set_data(x_index, y_index)
    artists.final_dot.set_data([x_index[-1]], [y_index[-1]])

    # Save once the endpoint returns close to its starting point.
    # Exact float equality is rare, so use a tolerance-based distance check.
    if len(state.pattern_points_x) > MIN_FRAMES_BEFORE_CLOSE_CHECK:
        dist_to_start = np.hypot(
            state.pattern_points_x[-1] - state.pattern_points_x[0],
            state.pattern_points_y[-1] - state.pattern_points_y[0],
        )
    else:
        dist_to_start = np.inf

    if dist_to_start <= START_TOLERANCE:
        save_pattern(state.pattern_points_x, state.pattern_points_y)
        raise SystemExit

    return artists.line, artists.final_dot


def main():
    """Load configuration, build the animation, and display it."""

    state = load_config()
    artists = create_figure()
    ani = animation.FuncAnimation(
        artists.fig,
        update,
        fargs=(state, artists),
        interval=0.50,
    )
    plt.show()
    return ani


if __name__ == "__main__":
    main()
