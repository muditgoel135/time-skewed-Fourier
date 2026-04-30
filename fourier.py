"""
This code creates an animated visualization of a Fourier series using matplotlib.
It defines a set of angles, lengths, and speeds for the Fourier series and computes the x and y coordinates based on these parameters.
The animation updates the angles over time, creating a dynamic pattern. The final point of the pattern is marked with a red 'x', and the trail of points is shown in black.
"""

# Import necessary libraries
import json
import pathlib
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Load angles, lengths, and speeds from config.json (edit that file to change the animation)
_cfg = json.loads(pathlib.Path("config.json").read_text())
angles = np.array(_cfg["angles"], dtype=float)
lengths = np.array(_cfg["lengths"], dtype=float)
speeds = np.array(_cfg["speeds"], dtype=float)
min_length = min(len(angles), len(lengths), len(speeds))
pattern_points_x = []
pattern_points_y = []


# Set up the figure and axes for the animation
fig, ax = plt.subplots()
(line,) = ax.plot([], [], marker="o", color="orange", markersize=3)
(final_dot,) = ax.plot([], [], "rx")
(trail_line,) = ax.plot([], [], marker="o", color="black", markersize=1)

# Set the limits and aspect ratio of the plot
ax.set_xlim(-10, 10)
ax.set_ylim(-10, 10)
ax.set_aspect("equal")
ax.grid()


def compute_points():
    """
    Compute the x and y coordinates of the points based on the current angles, lengths, and speeds

    :return: Two lists containing the x and y coordinates of the points
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
    Update the angles and compute the new points for the animation

    :param frame: The current frame number (not used in this function)
    :return: Updated line and final dot for the animation
    """

    # Update the angles based on the speeds and ensure they stay within 0-360 degrees
    global angles

    # Update angles and wrap them around using modulo 360
    for i in range(min_length):
        angles[i] += speeds[i]
        angles[i] = angles[i] % 360

    # Compute the new points based on the updated angles
    X_index, Y_index = compute_points()

    # Update the line and final dot with the new coordinates
    line.set_data(X_index, Y_index)
    final_dot.set_data([X_index[-1]], [Y_index[-1]])

    # Append the final point to the pattern points and update the trail line
    pattern_points_x.append(X_index[-1])
    pattern_points_y.append(Y_index[-1])

    # Update the trail line with the new pattern points
    trail_line.set_data(pattern_points_x, pattern_points_y)

    # Check if the pattern has completed a full cycle (returns to the starting point)
    if (
        pattern_points_x[-1] == pattern_points_x[0]
        and pattern_points_y[-1] == pattern_points_y[0]
        and len(pattern_points_x) > 1
    ):
        with open("output/pattern_points.txt", "w") as f:
            for x, y in zip(pattern_points_x, pattern_points_y):
                f.write(f"{x}, {y}\n")
        plt.savefig("output/Ending_Pattern.png")
        exit()

    return line, final_dot


# Create the animation
ani = animation.FuncAnimation(fig, update, interval=50)
plt.show()
