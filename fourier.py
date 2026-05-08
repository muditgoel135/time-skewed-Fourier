"""Animate a chain of rotating arms and save the completed traced pattern."""

import json
import math
import pathlib
import warnings

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Load the arm configuration. Matching indexes across the arrays describe one arm.
_cfg = json.loads(pathlib.Path("config.json").read_text())
angles = np.array(_cfg["angles"], dtype=float)
lengths = np.array(_cfg["lengths"], dtype=float)
speeds = np.array(_cfg["speeds"], dtype=float)
min_length = min(len(angles), len(lengths), len(speeds))
pattern_points_x = []
pattern_points_y = []
START_TOLERANCE = 1e-2
MIN_FRAMES_BEFORE_CLOSE_CHECK = 10
MAX_FRAMES = 100_000


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


def integer_speed_period():
    """
    Return the exact frame period when all active speeds are integer degrees.

    Each integer speed completes its own cycle after 360 / gcd(360, speed)
    frames. The whole arm chain returns to its starting angular state at the
    least common multiple of those per-arm periods. Return None when any active
    speed is fractional, because exact closure may not occur on an integer
    frame.
    """

    active_speeds = speeds[:min_length]
    if not np.all(np.isclose(active_speeds, np.round(active_speeds))):
        return None

    period = 1
    for speed in np.round(active_speeds).astype(int):
        arm_period = 1 if speed == 0 else 360 // math.gcd(360, abs(speed))
        period = math.lcm(period, arm_period)

    return period


EXACT_FRAME_COUNT = integer_speed_period()
FRAME_LIMIT = EXACT_FRAME_COUNT if EXACT_FRAME_COUNT is not None else MAX_FRAMES


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


def save_pattern():
    """Write the traced coordinates and current plot image to the output folder."""

    with open("output/pattern_points.txt", "w") as f:
        for x, y in zip(pattern_points_x, pattern_points_y):
            f.write(f"{x}, {y}\n")
    plt.savefig("output/Ending_Pattern.png")


def stop_animation():
    """Stop the animation event source and close the plot window."""

    if ani.event_source is not None:
        ani.event_source.stop()
    plt.close(fig)


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

    should_stop_at_limit = len(pattern_points_x) >= FRAME_LIMIT

    if dist_to_start <= START_TOLERANCE or should_stop_at_limit:
        if EXACT_FRAME_COUNT is None and should_stop_at_limit:
            warnings.warn(
                f"Pattern did not close within {MAX_FRAMES:,} frames; "
                "saving the partial trace and stopping.",
                RuntimeWarning,
            )
        save_pattern()
        stop_animation()

    return line, final_dot


ani = animation.FuncAnimation(fig, update, frames=FRAME_LIMIT, interval=0.50, repeat=False)
plt.show()
