"""Animate a chain of rotating arms and save the completed traced pattern."""

import argparse
import json
import math
import pathlib
from fractions import Fraction
from functools import reduce

import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np

OUTPUT_DIR = pathlib.Path("output")
POINT_DENSITY_DIVISOR = 20

angles = np.array([], dtype=float)
lengths = np.array([], dtype=float)
speeds = np.array([], dtype=float)
min_length = 0
pattern_points_x = []
pattern_points_y = []
CYCLE_TICKS = 1
SUBSTEPS_PER_TICK = 1
TOTAL_PATTERN_STEPS = 1
ANGLE_STEP = np.array([], dtype=float)
fig = None
ax = None
trail_line = None
line = None
final_dot = None


def lcm(a, b):
    """Return the least common multiple of two integers."""

    return abs(a * b) // math.gcd(a, b)


def calculate_cycle_ticks(vector_speeds):
    """
    Return the number of original speed ticks needed to close the pattern.

    Speeds close exactly once ``ticks * speed`` is a whole number of 360-degree
    rotations. Stationary arms do not affect the period. JSON numbers are
    converted through strings so decimal speeds such as 0.5 are handled as exact
    rationals instead of binary floating-point approximations.
    """

    moving_speeds = [
        Fraction(str(abs(speed))).limit_denominator()
        for speed in vector_speeds
        if not np.isclose(speed, 0)
    ]
    if not moving_speeds:
        return 1

    periods = [
        speed.denominator
        * 360
        // math.gcd(speed.numerator, speed.denominator * 360)
        for speed in moving_speeds
    ]
    return reduce(lcm, periods, 1)


def calculate_substeps(vector_count, vector_speeds):
    """
    Return how many points to plot for each original speed tick.

    Faster and more numerous vectors can bend the endpoint path more between
    frames, so both the vector count and fastest absolute speed increase the
    sampling density. For the old one-point-per-degree behavior this value was
    always 1, which is why many patterns produced 360 segments plus the closing
    point.
    """

    max_speed = max((abs(speed) for speed in vector_speeds), default=0)
    return max(1, math.ceil(vector_count * max_speed / POINT_DENSITY_DIVISOR))


def compute_endpoint_for_angles(vector_angles, vector_lengths):
    """Return the chain endpoint for the supplied angles and lengths."""

    radians = np.radians(np.array(vector_angles, dtype=float) % 360)
    x = np.sum(np.array(vector_lengths, dtype=float) * np.cos(radians))
    y = np.sum(np.array(vector_lengths, dtype=float) * np.sin(radians))
    return x, y


def generate_pattern_points(start_angles, vector_lengths, vector_speeds):
    """
    Return all endpoint points for one complete density-adjusted cycle.

    The returned lists include the initial endpoint and the final closing
    endpoint, so their length is ``cycle_ticks * substeps + 1``.
    """

    vector_count = min(len(start_angles), len(vector_lengths), len(vector_speeds))
    current_angles = np.array(start_angles[:vector_count], dtype=float)
    current_lengths = np.array(vector_lengths[:vector_count], dtype=float)
    current_speeds = np.array(vector_speeds[:vector_count], dtype=float)
    cycle_ticks = calculate_cycle_ticks(current_speeds)
    substeps = calculate_substeps(vector_count, current_speeds)
    total_steps = cycle_ticks * substeps
    angle_step = current_speeds / substeps if substeps else current_speeds

    x_points = []
    y_points = []
    for _ in range(total_steps + 1):
        x, y = compute_endpoint_for_angles(current_angles, current_lengths)
        x_points.append(x)
        y_points.append(y)
        current_angles = (current_angles + angle_step) % 360

    return x_points, y_points


def compute_points():
    """
    Return the joint coordinates for the current arm chain.

    The first point is the origin; each following point is the end of one arm.
    """

    x_index = [0]
    y_index = [0]
    x = 0
    y = 0
    for angle, length in zip(angles, lengths):
        x += length * np.cos(np.radians(angle % 360))
        y += length * np.sin(np.radians(angle % 360))
        x_index.append(x)
        y_index.append(y)

    return x_index, y_index


def save_pattern(x_points=None, y_points=None):
    """Write the traced coordinates and final image to the output directory."""

    x_points = pattern_points_x if x_points is None else x_points
    y_points = pattern_points_y if y_points is None else y_points

    OUTPUT_DIR.mkdir(exist_ok=True)
    with (OUTPUT_DIR / "pattern_points.txt").open("w") as f:
        for x, y in zip(x_points, y_points):
            f.write(f"{x}, {y}\n")
    plt.savefig(OUTPUT_DIR / "Ending_Pattern.png")


def update(frame):
    """
    Advance the animation by one substep and update the plotted artists.

    ``frame`` is used to detect the final planned sample so the saved pattern
    contains the full, density-adjusted cycle.
    """

    global angles

    angles = (angles + ANGLE_STEP) % 360

    x_index, y_index = compute_points()

    pattern_points_x.append(x_index[-1])
    pattern_points_y.append(y_index[-1])

    trail_line.set_data(pattern_points_x, pattern_points_y)

    line.set_data(x_index, y_index)
    final_dot.set_data([x_index[-1]], [y_index[-1]])

    if frame == TOTAL_PATTERN_STEPS - 1:
        save_pattern()
        plt.close(fig)

    return trail_line, line, final_dot


def load_config(config_path="config.json"):
    """Load and align arm arrays from a JSON configuration file."""

    cfg = json.loads(pathlib.Path(config_path).read_text())
    loaded_angles = np.array(cfg["angles"], dtype=float)
    loaded_lengths = np.array(cfg["lengths"], dtype=float)
    loaded_speeds = np.array(cfg["speeds"], dtype=float)
    vector_count = min(len(loaded_angles), len(loaded_lengths), len(loaded_speeds))
    return (
        loaded_angles[:vector_count],
        loaded_lengths[:vector_count],
        loaded_speeds[:vector_count],
        vector_count,
    )


def setup_plot():
    """Create the matplotlib figure and artists used by the animation."""

    global fig, ax, trail_line, line, final_dot

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


def initialize_from_config(config_path="config.json"):
    """Load configuration and compute the sampling plan globals."""

    global angles, lengths, speeds, min_length, pattern_points_x, pattern_points_y
    global CYCLE_TICKS, SUBSTEPS_PER_TICK, TOTAL_PATTERN_STEPS, ANGLE_STEP

    angles, lengths, speeds, min_length = load_config(config_path)
    pattern_points_x = []
    pattern_points_y = []
    CYCLE_TICKS = calculate_cycle_ticks(speeds)
    SUBSTEPS_PER_TICK = calculate_substeps(min_length, speeds)
    TOTAL_PATTERN_STEPS = CYCLE_TICKS * SUBSTEPS_PER_TICK
    ANGLE_STEP = speeds / SUBSTEPS_PER_TICK if SUBSTEPS_PER_TICK else speeds


def print_sampling_summary():
    """Print how many points will be saved for the current configuration."""

    max_speed = max((abs(speed) for speed in speeds), default=0)
    print(
        "Saving a cycle with "
        f"{TOTAL_PATTERN_STEPS + 1} points "
        f"({min_length} vectors, max speed {max_speed:g}, "
        f"{SUBSTEPS_PER_TICK} samples per speed tick)."
    )


def seed_animation_artists():
    """Set artist data to the starting chain state before animation begins."""

    initial_x, initial_y = compute_points()
    pattern_points_x.append(initial_x[-1])
    pattern_points_y.append(initial_y[-1])
    trail_line.set_data(pattern_points_x, pattern_points_y)
    line.set_data(initial_x, initial_y)
    final_dot.set_data([initial_x[-1]], [initial_y[-1]])


def save_without_animation():
    """Generate and save the completed pattern without opening an animation window."""

    global pattern_points_x, pattern_points_y

    setup_plot()
    pattern_points_x, pattern_points_y = generate_pattern_points(angles, lengths, speeds)
    chain_x, chain_y = compute_points()
    trail_line.set_data(pattern_points_x, pattern_points_y)
    line.set_data(chain_x, chain_y)
    final_dot.set_data([pattern_points_x[-1]], [pattern_points_y[-1]])
    save_pattern()
    plt.close(fig)


def main(config_path="config.json", save_only=False):
    """Run or save the Fourier arm animation for a local configuration."""

    initialize_from_config(config_path)
    print_sampling_summary()

    if save_only:
        save_without_animation()
        return None

    setup_plot()
    seed_animation_artists()

    ani = animation.FuncAnimation(
        fig,
        update,
        frames=TOTAL_PATTERN_STEPS,
        interval=0.50,
        repeat=False,
    )
    plt.show()
    return ani


def parse_args():
    """Return command-line arguments for running this script."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        default="config.json",
        help="Path to the arm configuration JSON file.",
    )
    parser.add_argument(
        "--save-only",
        action="store_true",
        help="Generate output files without opening an animation window.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    main(config_path=args.config, save_only=args.save_only)
