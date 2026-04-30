import numpy as np
import matplotlib.pyplot as plt

angles = np.array([160, 284, 308, 168, 249, 90, 201, 161, 8])
lengths = np.array([2, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8])
speeds = np.array([-1, 2, -3, 4, -5, 6, -7, 8, -9])
min_length = min(len(angles), len(lengths), len(speeds))
X = 0
Y = 0
X_index = []
Y_index = []
final_point = (0, 0)
all_points = []


def main_vars():
    global X, Y, X_index, Y_index, final_point, all_points

    X = sum(
        [lengths[i] * np.cos(np.radians(angles[i] % 360)) for i in range(min_length)]
    )

    Y = sum(
        [lengths[i] * np.sin(np.radians(angles[i] % 360)) for i in range(min_length)]
    )

    final_point = (X, Y)

    X_index = [0] + [
        sum([lengths[i] * np.cos(np.radians(angles[i] % 360)) for i in range(j + 1)])
        for j in range(min_length)
    ]

    Y_index = [0] + [
        sum([lengths[i] * np.sin(np.radians(angles[i] % 360)) for i in range(j + 1)])
        for j in range(min_length)
    ]

    all_points = list(zip(X_index, Y_index))

    print(X, "\n", Y, "\n", X_index, "\n", Y_index, "\n", final_point, "\n", all_points)


main_vars()


def plot_points():
    # Define global variables to access them within the function
    global X_index, Y_index

    # Plotting the points from the Fourier series
    plt.plot(
        X_index,
        Y_index,
        marker="o",
        color="orange",
        label="Points from Fourier Series",
        markersize=2.5,
    )

    plt.plot(
        [0, final_point[0] / min_length, final_point[0]],
        [0, final_point[1] / min_length, final_point[1]],
        color="green",
        label="Path to Final Point",
        marker="o",
        markersize=5,
    )

    plt.plot(
        final_point[0],
        final_point[1],
        marker="x",
        color="red",
        label="Final Point",
        markersize=10,
    )

    # Setting up the plot
    plt.title("Points from Fourier Series")
    plt.xlabel("X-axis")
    plt.ylabel("Y-axis")
    plt.grid()
    plt.axis("equal")  # Ensure equal aspect ratio
    plt.xlim(-10, 10)
    plt.ylim(-10, 10)
    plt.legend()

    # Display the plot
    plt.show()


plot_points()
