# time-skewed-Fourier

An animated visualization of a Fourier series built with Python and matplotlib. A chain of rotating arms traces a pattern over time; when the pattern closes into a full cycle the result is saved to disk.

## How it works

Each "arm" in the chain has three properties:

| Property  | Meaning                                                    |
| --------- | ---------------------------------------------------------- |
| `angles`  | Starting angle of the arm in degrees                       |
| `lengths` | Length of the arm                                          |
| `speeds`  | Degrees the arm rotates per frame (negative = clockwise)   |

Every frame, each arm's angle is incremented by its speed, the tip of the chain traces a point, and the accumulated trail is drawn in black. When the trail's current endpoint returns to its starting point the animation stops, saves the pattern image, and exits.

## Setup

**Requirements:** Python 3.8+

```bash
pip install -r requirements.txt
```

Create the output directory before running:

```bash
mkdir output
```

## Running

```bash
python fourier.py
```

## Configuration

Edit `config.json` to change the animation — no Python knowledge needed. Each index across the three arrays describes one arm:

```json
{
  "angles":  [315, 160, 284, ...],
  "lengths": [  1,   2, 1.1, ...],
  "speeds":  [  0,  -1,   2, ...]
}
```

- **Add an arm** — append one value to each of the three arrays.
- **Remove an arm** — delete the last value from each array.
- Arrays can have different lengths; the shortest one determines how many arms are used.

### Tips

- A `speed` of `0` keeps an arm stationary (acts as a fixed offset).
- Larger `lengths` make that arm dominate the shape.
- Mixing positive and negative speeds produces more complex, asymmetric patterns.
- All speeds that share a common factor will produce a closed loop sooner.

## Output

When the pattern completes a full cycle two files are written to the `output/` directory:

| File                           | Contents                                          |
| ------------------------------ | ------------------------------------------------- |
| `output/Ending_Pattern.png`    | Screenshot of the completed pattern               |
| `output/pattern_points.txt`    | All trail coordinates, one `x, y` pair per line   |

## Project structure

```text
fourier.py        # Animation script
config.json       # Editable arm configuration
requirements.txt  # Python dependencies
output/           # Generated output (create before running)
```
