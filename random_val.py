"""Generate a random arm configuration and write it to config.json."""

import random
import json

# Use one shared length so every generated arm has an angle, length, and speed.
length = random.randint(30, 50)
angles = [random.randint(0, 359) for _ in range(length)]
lengths = [random.uniform(0.1, 4.0) for _ in range(length)]
speeds = [random.randint(-10, 10) for _ in range(length)]

# Ensure the chain actually moves; an all-zero speed vector creates a static pattern.
if all(speed == 0 for speed in speeds):
    speeds[random.randrange(length)] = random.choice([-1, 1])

# This overwrites any existing config.json in the current directory.
with open("config.json", "w") as f:
    json.dump({"angles": angles, "lengths": lengths, "speeds": speeds}, f)
