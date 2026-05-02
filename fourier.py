"""Animate a chain of rotating arms and save the completed traced pattern."""

import json
import pathlib
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Load the arm configuration. Matching indexes across the arrays describe one arm.
_cfg = json.loads(pathlib.Path("config.json").read_text())
angles = np.array(_cfg["angles"], dtype=float)
initial_angles = angles.copy()
lengths = np.array(_cfg["lengths"], dtype=float)
speeds = np.array(_cfg["speeds"], dtype=float)
min_length = min(len(angles), len(lengths), len(speeds))
pattern_points_x = []
pattern_points_y = []
START_TOLERANCE = 1e-2
MIN_FRAMES_BEFORE_CLOSE_CHECK = 10
ANGLE_TOLERANCE_DEGREES = 1e-3


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


def compute_points():
    """
    Return the joint coordinates for the current arm chain.

    The first point is the origin; each following point is the end of one arm.
    """

    X_index = [0] + [
        sum([lengths[i] * np.cos(np.radians(angles[i] % 360)) for i in range(j + 1)])
        for j in range(min_length)
    ]

    Y_index = [0] + [
        sum([lengths[i] * np.sin(np.radians(angles[i] % 360)) for i in range(j + 1)])
        for j in range(min_length)
    ]

    return X_index, Y_index


def update(frame):
    """
    Advance the animation by one frame and update the plotted artists.

    The frame number is supplied by matplotlib but is not needed here.
    """

    global angles

    for i in range(min_length):
        angles[i] += speeds[i]
        angles[i] = angles[i] % 360

    X_index, Y_index = compute_points()

    pattern_points_x.append(X_index[-1])
    pattern_points_y.append(Y_index[-1])

    trail_line.set_data(pattern_points_x, pattern_points_y)

    line.set_data(X_index, Y_index)
    final_dot.set_data([X_index[-1]], [Y_index[-1]])

    # Save once the endpoint returns close to its starting point.
    # Exact float equality is rare, so use a tolerance-based distance check.
    if len(pattern_points_x) > MIN_FRAMES_BEFORE_CLOSE_CHECK:
        dist_to_start = np.hypot(
            pattern_points_x[-1] - pattern_points_x[0],
            pattern_points_y[-1] - pattern_points_y[0],
        )
    else:
        dist_to_start = np.inf

    angles_back_at_start = np.all(
        np.abs(((angles[:min_length] - initial_angles[:min_length] + 180) % 360) - 180)
        <= ANGLE_TOLERANCE_DEGREES
    )

    if dist_to_start <= START_TOLERANCE and angles_back_at_start:
        with open("output/pattern_points.txt", "w") as f:
            for x, y in zip(pattern_points_x, pattern_points_y):
                f.write(f"{x}, {y}\n")
        plt.savefig("output/Ending_Pattern.png")
        exit()

    return line, final_dot


ani = animation.FuncAnimation(fig, update, interval=0.50)
plt.show()
