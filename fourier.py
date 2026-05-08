"""Animate a chain of rotating arms and save the completed traced pattern."""

import json
import pathlib

import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np

START_TOLERANCE = 1e-2
MIN_FRAMES_BEFORE_CLOSE_CHECK = 10


def compute_points(angles, lengths):
    """
    Return the joint coordinates for an arm chain.

    The first point is the origin; each following point is the end of one arm.
    """

    arm_count = min(len(angles), len(lengths))
    x_index = [0] + [
        sum(lengths[i] * np.cos(np.radians(angles[i] % 360)) for i in range(j + 1))
        for j in range(arm_count)
    ]
    y_index = [0] + [
        sum(lengths[i] * np.sin(np.radians(angles[i] % 360)) for i in range(j + 1))
        for j in range(arm_count)
    ]

    return x_index, y_index


class FourierAnimationState:
    """Mutable state and frame update behavior for the Fourier animation."""

    def __init__(self, angles, lengths, speeds, trail_line, line, final_dot):
        self.angles = angles
        self.lengths = lengths
        self.speeds = speeds
        self.pattern_points_x = []
        self.pattern_points_y = []
        self.trail_line = trail_line
        self.line = line
        self.final_dot = final_dot
        self.arm_count = min(len(self.angles), len(self.lengths), len(self.speeds))

    def update(self, frame):
        """
        Advance the animation by one frame and update the plotted artists.

        The frame number is supplied by matplotlib but is not needed here.
        """

        for i in range(self.arm_count):
            self.angles[i] += self.speeds[i]
            self.angles[i] = self.angles[i] % 360

        x_index, y_index = compute_points(
            self.angles[: self.arm_count],
            self.lengths[: self.arm_count],
        )

        self.pattern_points_x.append(x_index[-1])
        self.pattern_points_y.append(y_index[-1])

        self.trail_line.set_data(self.pattern_points_x, self.pattern_points_y)
        self.line.set_data(x_index, y_index)
        self.final_dot.set_data([x_index[-1]], [y_index[-1]])

        # Save once the endpoint returns close to its starting point.
        # Exact float equality is rare, so use a tolerance-based distance check.
        if len(self.pattern_points_x) > MIN_FRAMES_BEFORE_CLOSE_CHECK:
            dist_to_start = np.hypot(
                self.pattern_points_x[-1] - self.pattern_points_x[0],
                self.pattern_points_y[-1] - self.pattern_points_y[0],
            )
        else:
            dist_to_start = np.inf

        if dist_to_start <= START_TOLERANCE:
            with open("output/pattern_points.txt", "w") as f:
                for x, y in zip(self.pattern_points_x, self.pattern_points_y):
                    f.write(f"{x}, {y}\n")
            plt.savefig("output/Ending_Pattern.png")
            exit()

        return self.line, self.final_dot


def main():
    """Load configuration, build the plot, and run the animation."""

    # Load the arm configuration. Matching indexes across arrays describe one arm.
    cfg = json.loads(pathlib.Path("config.json").read_text())
    angles = np.array(cfg["angles"], dtype=float)
    lengths = np.array(cfg["lengths"], dtype=float)
    speeds = np.array(cfg["speeds"], dtype=float)

    # Draw the traced endpoint, the arm chain, and the current endpoint marker.
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

    state = FourierAnimationState(angles, lengths, speeds, trail_line, line, final_dot)
    fig.animation = animation.FuncAnimation(fig, state.update, interval=0.50)
    plt.show()


if __name__ == "__main__":
    main()
