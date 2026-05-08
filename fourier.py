"""Animate a chain of rotating arms and save the completed traced pattern."""

import json
import pathlib
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
OUTPUT_DIR = pathlib.Path("output")
POINTS_PATH = OUTPUT_DIR / "pattern_points.txt"
IMAGE_PATH = OUTPUT_DIR / "Ending_Pattern.png"


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


def save_completed_pattern():
    """Persist the completed pattern using temporary files and atomic replacement."""

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    points_tmp = POINTS_PATH.with_name(f"{POINTS_PATH.name}.tmp")
    preferred_image_tmp = IMAGE_PATH.with_name(f"{IMAGE_PATH.name}.tmp")
    fallback_image_tmp = IMAGE_PATH.with_name(f"{IMAGE_PATH.stem}.tmp{IMAGE_PATH.suffix}")
    completed_tmp_paths = []

    try:
        with points_tmp.open("w") as f:
            for x, y in zip(pattern_points_x, pattern_points_y):
                f.write(f"{x}, {y}\n")
        completed_tmp_paths.append(points_tmp)

        try:
            plt.savefig(preferred_image_tmp, format="png")
            image_tmp = preferred_image_tmp
        except Exception:
            preferred_image_tmp.unlink(missing_ok=True)
            plt.savefig(fallback_image_tmp)
            image_tmp = fallback_image_tmp
        completed_tmp_paths.append(image_tmp)

        points_tmp.replace(POINTS_PATH)
        image_tmp.replace(IMAGE_PATH)
    except Exception:
        tmp_paths = {
            points_tmp,
            preferred_image_tmp,
            fallback_image_tmp,
            *completed_tmp_paths,
        }
        for tmp_path in tmp_paths:
            tmp_path.unlink(missing_ok=True)
        raise


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

    if dist_to_start <= START_TOLERANCE:
        save_completed_pattern()
        raise SystemExit

    return line, final_dot


ani = animation.FuncAnimation(fig, update, interval=0.50)
plt.show()
