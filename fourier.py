import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

angles = np.array([160, 284, 308, 168, 249, 90, 201, 161, 8], dtype=float)
lengths = np.array([2, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8], dtype=float)
speeds = np.array([-1, 2, -3, 4, -5, 6, -7, 8, -9], dtype=float)
min_length = min(len(angles), len(lengths), len(speeds))
pattern_points_x = []
pattern_points_y = []

fig, ax = plt.subplots()
(line,) = ax.plot([], [], marker="o", color="orange", markersize=3)
(final_dot,) = ax.plot([], [], "rx")
(trail_line,) = ax.plot([], [], marker="o", color="black", markersize=1)

ax.set_xlim(-10, 10)
ax.set_ylim(-10, 10)
ax.set_aspect("equal")
ax.grid()


def compute_points():
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
    global angles

    for i in range(min_length):
        angles[i] += speeds[i]
        angles[i] = angles[i] % 360

    X_index, Y_index = compute_points()

    line.set_data(X_index, Y_index)
    final_dot.set_data([X_index[-1]], [Y_index[-1]])

    pattern_points_x.append(X_index[-1])
    pattern_points_y.append(Y_index[-1])

    trail_line.set_data(pattern_points_x, pattern_points_y)

    if (
        pattern_points_x[-1] == pattern_points_x[0]
        and pattern_points_y[-1] == pattern_points_y[0]
        and len(pattern_points_x) > 1
    ):
        print(
            [
                (pattern_points_x, pattern_points_y)
                for i in range(len(pattern_points_x))
            ],
            end="\n",
        )
        plt.savefig()
        exit()
    return line, final_dot


ani = animation.FuncAnimation(fig, update, interval=50)
plt.show()
